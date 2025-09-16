import base64
import os, datetime, json
from datetime import datetime, timezone
import copy
import requests

import providers.smm_tool_provider
import providers.fhir_provider
import utils.mail_client


def set_document_metadata(fhir_resource, content_data, resource, content_counter=0):
    """
    Helper function to set category, extensions, and identifier for DocumentReference
    """
    # Inicializar category si no existe
    if "category" not in fhir_resource:
        fhir_resource["category"] = []
    
    categoryList = content_data.get("category", [])
    print(f"DEBUG: Processing categories: {categoryList}")
    
    # Si no es una lista, convertirla en lista
    if not isinstance(categoryList, list):
        categoryList = [categoryList] if categoryList else []
    
    for category_item in categoryList:
        if not category_item:
            continue
            
        category_name = "Unknown"
        if isinstance(category_item, dict):
            category_name = category_item.get("primaryDisplay", "Unknown")
        elif isinstance(category_item, str):
            category_name = category_item
        else:
            print(f"DEBUG: Unexpected category format: {category_item}")
            continue
            
        print(f"DEBUG: Setting category: {category_name}")
        categoryCode = "Unknown"
        if category_name == "Adverse Effects Management":
            categoryCode = "AE"
        elif category_name == "Medication and Disease Management":
            categoryCode = "MDM"
        elif category_name == "Medication Usage":
            categoryCode = "MU"
        elif category_name == "Other Information":
            categoryCode = "OTHER"
        elif category_name == "Storage":
            categoryCode = "STO"
        elif category_name == "Support Administration":
            categoryCode = "SA"
            
        # Evitar categorías duplicadas
        category_exists = False
        for existing_cat in fhir_resource["category"]:
            if existing_cat["coding"][0]["code"] == categoryCode:
                category_exists = True
                break
                
        if not category_exists:
            fhir_resource["category"].append({
                "coding": [
                    {
                        "system": "http://hl7.eu/fhir/ig/gravitate-health/CodeSystem/DocumentReferenceCategory",
                        "code": categoryCode,
                        "display": category_name
                    }
                ]
            })
            print(f"DEBUG: Added category code: {categoryCode}")

    valueCode = "URL"
    if resource.get("contentMIMEtype") and len(resource["contentMIMEtype"]) > 0:
        mime_type = resource["contentMIMEtype"][0]["primaryDisplay"]
        if mime_type == "image/png":
            valueCode = "image"
        elif mime_type == "application/pdf":
            valueCode = "document"
        elif mime_type == "text/plain":
            valueCode = "text"
        elif "video" in mime_type:
            valueCode = "video"

    fhir_resource["content"][content_counter]["attachment"]["extension"] = [
        {
            "url": "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/VisualizationMethod",
            "valueCode": valueCode 
        }
    ]
    fhir_resource["content"][content_counter]["attachment"]["title"] = content_data.get("description", "No title available")
    fhir_resource["identifier"] = [
        {
            "system": "http://example.org",
            "value": fhir_resource["id"]
        }
    ]


def compare_document_references(existing_resource, new_resource):
    """
    Compara dos recursos DocumentReference para determinar si hay cambios significativos
    Args:
        existing_resource (dict): Recurso existente en el servidor FHIR
        new_resource (dict): Nuevo recurso a comparar
    Returns:
        tuple: (needs_update: bool, changes: list)
    """
    needs_update = False
    changes = []
    
    # Comparar descripción
    existing_desc = existing_resource.get("description", "")
    new_desc = new_resource.get("description", "")
    if existing_desc != new_desc:
        changes.append(f"Description: '{existing_desc}' -> '{new_desc}'")
        needs_update = True
    
    # Comparar subject (manejar casos None de forma más inteligente)
    existing_subject = existing_resource.get("subject", {})
    new_subject = new_resource.get("subject", {})
    
    # Solo comparar subject si ambos tienen valores válidos
    if existing_subject and new_subject:
        existing_ref = existing_subject.get("reference", "")
        new_ref = new_subject.get("reference", "")
        if existing_ref != new_ref:
            changes.append(f"Subject reference: '{existing_ref}' -> '{new_ref}'")
            needs_update = True
            
        existing_display = existing_subject.get("display", "")
        new_display = new_subject.get("display", "")
        if existing_display != new_display:
            changes.append(f"Subject display: '{existing_display}' -> '{new_display}'")
            needs_update = True
    elif existing_subject and not new_subject:
        # Caso especial: tenía subject pero ahora no tiene
        # Solo marcamos como cambio si el existing_subject tenía contenido útil
        if existing_subject.get("reference") or existing_subject.get("display"):
            changes.append(f"Subject removed: '{existing_subject}' -> 'None'")
            needs_update = True
    elif not existing_subject and new_subject:
        # Caso especial: no tenía subject pero ahora sí tiene
        if new_subject.get("reference") or new_subject.get("display"):
            changes.append(f"Subject added: 'None' -> '{new_subject}'")
            needs_update = True
    
    # Comparar número de archivos de contenido
    existing_content_count = len(existing_resource.get("content", []))
    new_content_count = len(new_resource.get("content", []))
    if existing_content_count != new_content_count:
        changes.append(f"Content count: {existing_content_count} -> {new_content_count}")
        needs_update = True
    
    # Comparar contenido detalladamente
    existing_content = existing_resource.get("content", [])
    new_content = new_resource.get("content", [])
    
    for i, content in enumerate(new_content):
        if i < len(existing_content):
            existing_attachment = existing_content[i].get("attachment", {})
            new_attachment = content.get("attachment", {})
            
            # Comparar URL
            existing_url = existing_attachment.get("url", "")
            new_url = new_attachment.get("url", "")
            if existing_url != new_url:
                changes.append(f"Content {i} URL: '{existing_url}' -> '{new_url}'")
                needs_update = True
            
            # Comparar contentType
            existing_type = existing_attachment.get("contentType", "")
            new_type = new_attachment.get("contentType", "")
            if existing_type != new_type:
                changes.append(f"Content {i} type: '{existing_type}' -> '{new_type}'")
                needs_update = True
            
            # Comparar language
            existing_lang = existing_attachment.get("language", "")
            new_lang = new_attachment.get("language", "")
            if existing_lang != new_lang:
                changes.append(f"Content {i} language: '{existing_lang}' -> '{new_lang}'")
                needs_update = True
    
    return needs_update, changes


def connector_smm_tool(mail_client: utils.mail_client.Mail_client):
    print("DEBUG: Starting connector_smm_tool function")
    smm_server_url = os.getenv("SMM_SERVER_URL")
    object_storage_url = os.getenv("OBJECT_STORAGE_URL")
    smm_app_id = os.getenv("SMM_APP_ID")
    smm_table_id = os.getenv("SMM_TABLE_ID")
    smm_api_key = os.getenv("SMM_API_KEY")
    print(f"DEBUG: Environment variables loaded - SMM_SERVER_URL: {smm_server_url is not None}")
    
    smm_tool_provider = providers.smm_tool_provider.SmmToolProvider(smm_server_url, object_storage_url, smm_app_id, smm_table_id, smm_api_key)
    
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
    fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)
    print(f"DEBUG: Providers initialized successfully")

    ## TODO de-hardcode this
    smm_resources, errors = smm_tool_provider.get_all_smm()
    print(f"DEBUG: Retrieved {len(smm_resources) if smm_resources else 0} SMM resources")
    if smm_resources is None:
        print("Error occurred fetching SMM resources")
        print(errors)
        if mail_client != None:
            mail_client.create_message(errors)
            print("Error occurred, email sent")
        return

    smm_fhir_resources = []
    for resource in smm_resources:
        print("____________________ NEW RESOURCE _______________________")
        print(f"DEBUG: Resource keys: {list(resource.keys())}")  # Debug: mostrar las claves disponibles
        fhir_resource = {}
        fhir_resource["id"] = resource["_id"].replace("_", "")[0:63]
        fhir_resource["resourceType"] = "DocumentReference"
        fhir_resource["status"] = "current"
        fhir_resource["docStatus"] = "final"
        fhir_resource["description"] = resource.get("description", "No description available")
        fhir_resource["meta"] = {
            "profile": [
                "http://hl7.eu/fhir/ig/gravitate-health/StructureDefinition/AdditionalSupportMaterial"
            ]
        }
        fhir_resource["category"] = []
        
        try:
            # Verificar si 'subject' existe y no es None
            if "subject" in resource and resource["subject"] is not None and len(resource["subject"]) > 0:
                subject_row_id = resource["subject"][0]["_id"]
                subject_table_split = subject_row_id.split("_")
                subject_table_id = f"{subject_table_split[1]}_{subject_table_split[2]}"
                subject_row, subject_errors = smm_tool_provider.get_row_by_id(subject_table_id, subject_row_id)

                if subject_row:
                    print(f"DEBUG: Subject data retrieved for row {subject_row_id}: {subject_row}")
                    subject = subject_row.get("Reference", None)
                    if subject:
                        print(f"DEBUG: Subject data found: {subject}")
                    try:
                        # Subject is expected to be a reference string like "Bundle/id"
                        if isinstance(subject, str) and "/" in subject:
                            subject_resource_type = subject.split("/")[0]
                            subject_resource_id = subject.split("/")[1]

                            print(f"DEBUG: Subject resource type: {subject_resource_type}, ID: {subject_resource_id}")
                            
                            # Get Bundle from FHIR Server
                            bundle_object = fhir_provider.get_resource_by_id(subject_resource_type, subject_resource_id)
                            if bundle_object and bundle_object.get("resourceType") == "Bundle":
                                # Try to extract MedicinalProductDefinition reference from Bundle
                                entries = bundle_object.get("entry", [])
                                print(f"Entries: {entries}")
                                print(f"DEBUG: Bundle entries found: {len(entries)}")
                                medicinal_product_definition = ""
                                display_name = ""
                                
                                for entry in entries:
                                    resource_in_bundle = entry.get("resource", {})
                                    print(f"DEBUG: Resource found in bundle: {resource_in_bundle}")
                                    if resource_in_bundle.get("resourceType") == "Composition":
                                        composition_subjects = resource_in_bundle.get("subject", [])
                                        print(f"DEBUG: Composition subjects found: {composition_subjects}")
                                        if composition_subjects:
                                            medicinal_product_definition = composition_subjects[0].get("reference", "")
                                            print(f"DEBUG: MedicinalProductDefinition found: {medicinal_product_definition}")
                                            break
                                
                                # Get display name from Bundle metadata or first entry
                                if entries:
                                    first_resource = entries[0].get("resource", {})
                                    if first_resource.get("resourceType") == "Composition":
                                        display_name = first_resource.get("title", "")
                                
                                if medicinal_product_definition:
                                    fhir_resource["subject"] = {
                                        "reference": medicinal_product_definition,
                                        "display": display_name or f"Bundle/{subject_resource_id}"
                                    }
                                else:
                                    # Fallback to Bundle reference
                                    fhir_resource["subject"] = {
                                        "reference": f"Bundle/{subject_resource_id}",
                                        "display": display_name or f"Bundle/{subject_resource_id}"
                                    }
                            else:
                                print(f"DEBUG: Bundle not found or invalid for subject {subject}")
                                fhir_resource["subject"] = {
                                    "reference": subject,
                                    "display": subject
                                }
                        else:
                            # If subject is not in expected format, use it as-is
                            print(f"DEBUG: Subject format unexpected: {subject}")
                            if isinstance(subject, dict) and "primaryDisplay" in subject:
                                # Handle subject as dictionary with primaryDisplay
                                reference = subject.get("Reference", f"Unknown/{subject_row_id}")
                                display = subject.get("primaryDisplay", "Unknown")
                                fhir_resource["subject"] = {
                                    "reference": reference,
                                    "display": display
                                }
                            else:
                                # Last fallback
                                fhir_resource["subject"] = {
                                    "reference": f"Unknown/{subject_row_id}",
                                    "display": str(subject) if subject else "Unknown"
                                }
                    except Exception as bundle_error:
                        print(f"Error processing Bundle for subject: {bundle_error}")
                        # Fallback to basic subject reference
                        fhir_resource["subject"] = {
                            "reference": f"Bundle/{subject_row_id}",
                            "display": f"Bundle/{subject_row_id}"
                        }
                else:
                    print(f"DEBUG: Could not retrieve subject data for row {subject_row_id}")
            else:
                print("DEBUG: 'subject' field not found, is None, or empty in resource")
        except Exception as e:
            print(f"Error getting subject: {e}")
            print(f"DEBUG: resource['subject'] = {resource.get('subject', 'FIELD_NOT_FOUND')}")
            pass
        # TODO: Ignore Author for now. Change in future
        #try:
        #    fhir_resource["author"] = {
        #        "reference": resource["author"][0]["primaryDisplay"],
        #        "display": resource["author"][0]["primaryDisplay"]
        #    }
        #except:
        #    pass
        fhir_resource["content"] = [
            {
                "attachment": {
                    "contentType": "",
                    "language": "",
                    "url": ""
                }
            }
        ]
        
        # Configurar contentType de forma segura
        try:
            if "contentMIMEtype" in resource and resource["contentMIMEtype"] is not None:
                fhir_resource["content"][0]["attachment"]["contentType"] = resource["contentMIMEtype"][0]["primaryDisplay"]
        except Exception as e:
            print(f"Error setting contentType: {e}")
            pass
            
        # Configurar language de forma segura
        try:
            if "language" in resource and resource["language"] is not None:
                fhir_resource["content"][0]["attachment"]["language"] = resource["language"][0]["primaryDisplay"]
        except Exception as e:
            print(f"Error setting language: {e}")
            pass
            
        # Manejar contenido remoto o local de forma segura
        try:
            print(f"DEBUG: Processing content - isRemote: {resource.get('isRemote')}")
            print(f"DEBUG: Resource contentData: {resource.get('contentData', 'NOT_FOUND')}")
            print(f"DEBUG: Resource contentURL: {resource.get('contentURL', 'NOT_FOUND')}")
            
            if resource.get("isRemote") is True:
                print("DEBUG: Processing remote content")
                if "contentURL" in resource:
                    fhir_resource["content"][0]["attachment"]["url"] = resource["contentURL"]
                    print(f"DEBUG: Set remote URL: {resource['contentURL']}")
                    
                    # Para contenido remoto, intentar obtener metadatos de diferentes fuentes
                    content_data = None
                    if "contentData" in resource and resource["contentData"] is not None and len(resource["contentData"]) > 0:
                        content_data = resource["contentData"][0]
                        print(f"DEBUG: Found contentData for remote: {content_data}")
                    else:
                        # Si no hay contentData, crear uno básico usando información del recurso principal
                        print("DEBUG: No contentData found, creating basic metadata from main resource")
                        content_data = {
                            "category": resource.get("category", "Other Information"),
                            "description": resource.get("description", "No title available")
                        }
                        print(f"DEBUG: Created basic content_data: {content_data}")
                    
                    if content_data:
                        print(f"DEBUG: Category found: {content_data.get('category', 'Unknown')}")
                        # Usar la función helper para establecer metadatos
                        set_document_metadata(fhir_resource, content_data, resource, 0)
                        print(f"DEBUG: Applied metadata for remote content")
                    else:
                        print("DEBUG: No content data available for remote content")
            elif resource.get("isRemote") is False:
                print("DEBUG: Processing local content")
                if "contentData" in resource and resource["contentData"] is not None:
                    content_counter = 0
                    for content in resource["contentData"]:
                        try:
                            if(content_counter > 0):
                                fhir_resource["content"].append(copy.deepcopy(fhir_resource["content"][0]))
                            response, errors = smm_tool_provider.get_file_from_budibase(content["url"])
                            if response:
                                response.raise_for_status()
                                file_name = content["key"].split("/")[2]
                                response_create_object, errors = smm_tool_provider.create_object_in_bucket(response.content,{
                                    "resourceName": file_name,
                                    "description" : fhir_resource["description"],
                                        "attachment" : {
                                            "contentType" : response.headers.get("Content-Type", "application/octet-stream"), 
                                            "language" : fhir_resource["content"][0]["attachment"].get("language", ""), 
                                            "creation" : datetime.now(timezone.utc).isoformat(),
                                    }
                                })
                                
                                # Configurar URL y contentType para contenido local
                                fhir_resource["content"][content_counter]["attachment"]["url"] = f"{object_storage_url}/resource/{file_name}"
                                fhir_resource["content"][content_counter]["attachment"]["contentType"] = resource["contentMIMEtype"][0]["primaryDisplay"]
                                
                                # Usar la función helper para establecer metadatos
                                set_document_metadata(fhir_resource, content, resource, content_counter)
                                print(f"DEBUG: Applied metadata for local content {content_counter}")
                        except requests.RequestException as e:
                            print(f"Error fetching content from {content.get('url', 'unknown URL')}: {e}")
                        except Exception as e:
                            print(f"Error processing content: {e}")
                        content_counter += 1
            else:
                print(f"DEBUG: Unknown isRemote value: {resource.get('isRemote')}")
        except Exception as e:
            print(f"Error processing content (isRemote/contentData): {e}")
            pass
        smm_fhir_resources.append(fhir_resource)

    for fhir_resource in smm_fhir_resources:
        # Buscar si ya existe un DocumentReference con el mismo ID
        existing_resource = None
        try:
            existing_resource = fhir_provider.get_resource_by_id("DocumentReference", fhir_resource["id"])
        except Exception as e:
            print(f"DocumentReference with ID {fhir_resource['id']} not found: {e}")

        # Si no se encuentra por ID, intentar buscar por descripción como respaldo
        if not existing_resource and fhir_resource.get("description"):
            # Buscar todos los DocumentReference y filtrar por descripción
            try:
                all_document_refs = fhir_provider.get_fhir_all_resource_type_from_server("DocumentReference")
                for doc_ref_entry in all_document_refs:
                    doc_ref = doc_ref_entry.get("resource", {})
                    if doc_ref.get("description") == fhir_resource["description"]:
                        existing_resource = doc_ref
                        break
            except Exception as e:
                print(f"Error finding DocumentReference by description: {e}")
            if existing_resource:
                print(f"Found existing DocumentReference by description: '{fhir_resource['description']}'")
        
        if existing_resource:
            if not existing_resource.get('id'):
                print(f"WARNING: existing_resource found but missing 'id'. Resource content: {existing_resource}")
            existing_id = existing_resource.get('id', 'unknown')
            print(f"DocumentReference with id {existing_id} already exists. Updating...")
            
            # Estrategia especial: si el nuevo recurso no tiene subject pero el existente sí,
            # preservar el subject existente para evitar perder información válida
            if not fhir_resource.get("subject") and existing_resource.get("subject"):
                print("Preserving existing subject as new resource processing failed to generate one")
                fhir_resource["subject"] = existing_resource["subject"]
            
            # Si encontramos el recurso por descripción, usar el ID existente
            if existing_resource.get("id") and existing_resource["id"] != fhir_resource["id"]:
                print(f"Using existing ID {existing_resource['id']} instead of {fhir_resource['id']}")
                fhir_resource["id"] = existing_resource["id"]
            
            # Preservar metadatos del recurso existente si están disponibles
            if "meta" in existing_resource:
                fhir_resource["meta"] = existing_resource["meta"]

        
            print(f"Resulting resource after merging: {json.dumps(fhir_resource, indent=2)}")

            print(f"Updating DocumentReference with id {existing_id}")
            error = fhir_provider.write_fhir_resource_to_server(fhir_resource, DESTINATION_SERVER)
        else:
            print(f"Creating new DocumentReference with id {fhir_resource['id']}")
            error = fhir_provider.write_fhir_resource_to_server(fhir_resource, DESTINATION_SERVER)
    
    fhir_provider.run_reindex_job()
    mail_client.create_message(errors)
    return smm_fhir_resources, errors
