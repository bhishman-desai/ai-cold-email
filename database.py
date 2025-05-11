import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB password from environment variable
db_password = os.getenv('MONGODB_PASSWORD')
if not db_password:
    raise ValueError("MONGODB_PASSWORD environment variable is not set")

connection_string = f"mongodb+srv://coldemail:{db_password}@cluster0.ingjjwc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
db = client.get_database('ColdEmail')
contacts = db.get_collection('contacts')

def save_contact(name, email_found, domain, email=None):
    try:
        contact = {
            'name': name,
            'email_found': email_found,
            'email': email,
            'domain': domain,
            'date': datetime.utcnow()
        }
        # Insert the contact and let MongoDB auto-generate the _id
        contacts.insert_one(contact)
        return True
    except Exception as e:
        print(f"Error saving contact: {str(e)}")
        return False

def contact_exists(name):
    try:
        contact = contacts.find_one({'name': name})
        return bool(contact)
    except Exception as e:
        print(f"Error checking contact: {str(e)}")
        return False

def cleanup_old_records():
    """Delete records older than 2 weeks"""
    try:
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        contacts.delete_many({'date': {'$lt': two_weeks_ago}})
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

# contacts.delete_many({})  # Clear the collection for testing purposes
# save_contact("John Doe", True, "bpdatal5@gmail.com")