import os
from dotenv import load_dotenv
import requests
from urllib.parse import quote

load_dotenv()

def get_email(name, company):
    """
    Get email using GetProspect API
    """
    api_key = os.getenv('GETPROSPECT_API_KEY')
    if not api_key:
        raise ValueError("GetProspect API key not found in environment variables")
    
    # URL encode the name and company
    encoded_name = quote(name)
    encoded_company = quote(company)
    
    url = f"https://api.getprospect.com/public/v1/email/find?name={encoded_name}&company={encoded_company}"
    
    headers = {
        "accept": "application/json",
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # You might want to add more error handling based on the API response structure
        if 'email' in data:
            return data['email']
        return None
    except Exception as e:
        print(f"Error getting email from GetProspect: {str(e)}")
        return None
