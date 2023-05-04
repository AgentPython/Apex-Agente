import jsonwebtoken as jwt
import requests
import pandas as pd

from time import time
from hashlib import sha256
from base64 import b64encode

data = {
    "base_url": "https://ohbypl.manage.trendmicro.com/",
    "application_id": "3A8C6F1D-5D9A-4157-A933-BF3554464F8C",
    "api_key": "E2758DF0-1F8E-41B7-8579-17D46D21E18C",
    "product_agent_api_path": "/WebApp/API/AgentResource/ProductAgents"
}

default_headers = ""
query = "?hostname"
http_method = "GET"
body = ""

raw_url = data['product_agent_api_path'] + query
url = data['base_url'] + raw_url

def create_checksum() -> str:
    string_to_hash = http_method.upper() + '|' + raw_url.lower() + '|' + default_headers + '|' + body
    hash_object = sha256(str.encode(string_to_hash))
    base64_string = b64encode(hash_object.digest()).decode('utf-8')
    return base64_string

def create_jwt_token(iat=time(), algorithm='HS256', version='V1') -> str:
    checksum = create_checksum()
    payload = {
        "appid": data['application_id'],
        "iat": iat,
        "version": version,
        "checksum": checksum
    }
    token = jwt.encode(payload, data['api_key'], algorithm=algorithm)
    return token

def fetch_data() -> list[dict]:
    jwt_token = create_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    res = requests.get(url, headers=headers, verify=False)
    return res.json()['result_content']

def create_data() -> dict[str, list]:
    data = fetch_data()
    data_list = {"Host Name": [], "Entity ID": [], "IP Address": [], "Last Registration Time": [], "Status": []}
    for d in data:
        data_list['Host Name'].append(d['host_name'])
        data_list['Entity ID'].append(d['entity_id'])
        data_list['IP Address'].append(d['ip_address_list'])
        data_list['Last Registration Time'].append(d['last_registration_time'])
        data_list['Status'].append(d['connection_status'].upper())

    return data_list


new_data = create_data()
ApexAgente = pd.DataFrame(new_data)
print(ApexAgente)
