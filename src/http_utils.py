import requests

def put_request(url, body):
    try:
        response = requests.put(url,json=body)
        if(response.status_code != 201):
            print("Error in HTTP PUT resource")
    except Exception as error:
        print(error)
    return