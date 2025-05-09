import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def get_email(full_name, domain):
    """
    Get email from hunter.io API
    """
    api_key = os.getenv('GETEMAIL_API_KEY')
    url = f"https://api.getemail.io/v1/email"
    
    params = {
        'api_key': api_key,
        'name': full_name,
        'domain': domain
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('email')
    except Exception as e:
        print(f"Error getting email: {str(e)}")
    
    return None
