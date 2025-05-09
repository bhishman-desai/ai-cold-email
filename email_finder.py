import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def get_email(full_name, domain, enrich=False):
    """
    Get email from getemail.io API using POST request
    
    Args:
        full_name (str): Full name of the prospect
        domain (str): Company or website domain
        enrich (bool): Whether to fetch additional contact info
    
    Returns:
        dict: Response data if successful, None otherwise
    """
    api_key = os.getenv('GETEMAIL_API_KEY')
    url = "https://api.getemail.io/dash/find-email"
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'fullname': full_name,
        'domain': domain
    }
    
    if enrich:
        payload['isEnrichToDo'] = True
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data
    except Exception as e:
        print(f"Error getting email: {str(e)}")
    
    return None