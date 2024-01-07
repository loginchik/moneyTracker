import os

from fastapi import Security, status, HTTPException
from fastapi.security import APIKeyQuery

with open(os.path.abspath('api_keys.txt')) as keys_file:
    API_KEYS = keys_file.read().split('\n')


api_key_query = APIKeyQuery(name='apikey', auto_error=False)


def get_api_key(api_key_query: str = Security(api_key_query)) -> str:
    if api_key_query in API_KEYS:
        return api_key_query
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Invalid or missing API Key'
    )