import requests
import logging 
def put_request(url, body):
    try:
        response = requests.put(url,json=body)
    except Exception as error:
        logging.error(error)
        logging.error(f"[HTTP ERROR] Error loading {body['resourceType']} with id {body['id']} to: {url}")
        return
    
    if(response.status_code not in [200, 201]):
        issue_list = response.json()["issue"]
        for issue in issue_list:
            resource_id = body["id"]
            resource_type = body["resourceType"]
            issue_severity = issue["severity"].upper()
            issue_diagnostic = issue["diagnostics"]
            logging.warning(f"{issue_severity}: {resource_type} with id {resource_id} || Status_code {response.status_code} || Reason: {issue_diagnostic}")
    return