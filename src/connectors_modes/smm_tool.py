import base64
import os, datetime, json
from datetime import datetime, timezone
import copy
import requests

import providers.smm_tool_provider
import providers.fhir_provider
import utils.mail_client


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
    smm_server_url = os.getenv("SMM_SERVER_URL")
    object_storage_url = os.getenv("OBJECT_STORAGE_URL")
    smm_app_id = os.getenv("SMM_APP_ID")
    smm_table_id = os.getenv("SMM_TABLE_ID")
    smm_api_key = os.getenv("SMM_API_KEY")
    smm_tool_provider = providers.smm_tool_provider.SmmToolProvider(smm_server_url, object_storage_url, smm_app_id, smm_table_id, smm_api_key)
    
    DESTINATION_SERVER = os.getenv("DESTINATION_SERVER")
    fhir_provider = providers.fhir_provider.FhirProvider(DESTINATION_SERVER)
    

    ## TODO de-hardcode this
    smm_resources, errors = smm_tool_provider.get_all_smm()
    if smm_resources is None:
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
            if resource.get("isRemote") is True:
                if "contentURL" in resource:
                    fhir_resource["content"][0]["attachment"]["url"] = resource["contentURL"]
            elif resource.get("isRemote") is False:
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
                                    #"author": "X-Plain Patient Education",
                                    "description" : fhir_resource["description"],
                                        "attachment" : {
                                            "contentType" : response.headers.get("Content-Type", "application/octet-stream"), 
                                            "language" : fhir_resource["content"][0]["attachment"].get("language", ""), 
                                            #"url" : "hello.com",  
                                            #"size" : "", 
                                            #"hash" : "ADE1234FE", 
                                            #"title" : "How to take Xarelto", 
                                            "creation" : datetime.now(timezone.utc).isoformat(),
                                    }
                                })
                                fhir_resource["content"][content_counter]["attachment"]["url"] = f"{object_storage_url}/resource/{file_name}"
                                fhir_resource["content"][content_counter]["attachment"]["contentType"] = response.headers.get("Content-Type", "application/octet-stream").split(";")[0]
                        except requests.RequestException as e:
                            print(f"Error fetching content from {content.get('url', 'unknown URL')}: {e}")
                        except Exception as e:
                            print(f"Error processing content: {e}")
                        content_counter += 1
        except Exception as e:
            print(f"Error processing content (isRemote/contentData): {e}")
            pass
        smm_fhir_resources.append(fhir_resource)

    for fhir_resource in smm_fhir_resources:
        # Buscar si ya existe un DocumentReference con el mismo ID
        existing_resource = fhir_provider.search_document_reference_by_id(fhir_resource["id"])
        
        # Si no se encuentra por ID, intentar buscar por descripción como respaldo
        if not existing_resource and fhir_resource.get("description"):
            existing_resource = fhir_provider.search_document_reference_by_criteria(
                description=fhir_resource["description"]
            )
            if existing_resource:
                print(f"Found existing DocumentReference by description: '{fhir_resource['description']}'")
        
        if existing_resource:
            print(f"DocumentReference with id {existing_resource['id']} already exists. Checking for updates...")
            
            # Estrategia especial: si el nuevo recurso no tiene subject pero el existente sí,
            # preservar el subject existente para evitar perder información válida
            if not fhir_resource.get("subject") and existing_resource.get("subject"):
                print("Preserving existing subject as new resource processing failed to generate one")
                fhir_resource["subject"] = existing_resource["subject"]
            
            # Usar la función de comparación mejorada
            needs_update, changes = compare_document_references(existing_resource, fhir_resource)
            
            # Filtrar cambios que son realmente regresiones (perder información válida)
            filtered_changes = []
            should_update = False
            
            for change in changes:
                # Evitar actualizaciones que eliminan subject válido
                if "Subject" in change and "-> 'None'" in change:
                    print(f"Skipping potentially regressive change: {change}")
                    continue
                else:
                    filtered_changes.append(change)
                    should_update = True
            
            if should_update and filtered_changes:
                print(f"Significant changes detected for DocumentReference with id {existing_resource['id']}:")
                for change in filtered_changes:
                    print(f"  - {change}")
                
                # Si encontramos el recurso por descripción, usar el ID existente
                if existing_resource["id"] != fhir_resource["id"]:
                    print(f"Using existing ID {existing_resource['id']} instead of {fhir_resource['id']}")
                    fhir_resource["id"] = existing_resource["id"]
                
                # Preservar metadatos del recurso existente si están disponibles
                if "meta" in existing_resource:
                    fhir_resource["meta"] = existing_resource["meta"]
                
                print(f"Updating DocumentReference with id {existing_resource['id']}")
                error = fhir_provider.write_fhir_resource_to_server(fhir_resource, DESTINATION_SERVER)
            else:
                print(f"No significant changes detected for DocumentReference with id {existing_resource['id']}. Skipping update.")
        else:
            print(f"Creating new DocumentReference with id {fhir_resource['id']}")
            error = fhir_provider.write_fhir_resource_to_server(fhir_resource, DESTINATION_SERVER)
    fhir_provider.run_reindex_job()
    mail_client.create_message(errors)
    return smm_fhir_resources, errors
