from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from database import contact_exists, save_contact, cleanup_old_records
from email_finder import get_email
from email_sender import send_email
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

# Configuration for contact limits
MIN_CONTACTS = 0  # Start processing from this position
MAX_CONTACTS = 2  # Stop after processing this many contacts
TOTAL_PROCESSED = 0  # Keep track of processed contacts

def setup_driver():
    chrome_options = Options()
    # Don't use headless mode since we need manual login
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_linkedin():
    """
    Open LinkedIn and wait for manual login
    """
    driver = setup_driver()
    print("Opening LinkedIn for manual login...")
    driver.get("https://www.linkedin.com/login")
    
    # Wait for successful login by checking for the presence of the search bar
    print("Please log in manually in the browser window...")
    print("Waiting for login to complete...")
    
    try:
        WebDriverWait(driver, 300).until(  # 5 minute timeout
            EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
        )
        print("Successfully logged in!")
        return driver
    except Exception as e:
        print("Login timeout or error occurred")
        driver.quit()
        raise e

def process_with_llm(text):
    """
    Process text with Hugging Face Inference API using Mistral 7B Chat format
    """
    API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3/v1/chat/completions"
    headers = {"Authorization": "Bearer " + os.getenv("HUGGINGFACE_API_KEY")}

    prompt = f"""Extract the name and company domain from this LinkedIn profile text. Domanin should be the main company name from their current position and in @company format which exists. 
    Return JSON format with 'name' and 'domain' keys. 
    
    Text: {text}
    
    Example response:
    {{"name": "John Doe", "domain": "@google.com"}}"""

    payload = {
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "temperature": 0.1  # Add parameters for more consistent output
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # Extract the generated content
        generated_text = response.json()["choices"][0]["message"]["content"]
        
        # Clean the response to get valid JSON
        json_str = generated_text.split("{")[1].split("}")[0]
        json_str = "{" + json_str + "}"
        
        return json.loads(json_str)
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return None

def process_linkedin_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # Find all person containers using data attribute
    person_cards = soup.find_all('div', {'data-chameleon-result-urn': True})
    
    for card in person_cards:
        try:
            # Extract raw text content
            text_content = ' '.join(card.stripped_strings)
            
            # Get structured data using LLM
            parsed_data = process_with_llm(text_content)
            
            if parsed_data:
                results.append({
                    'name': parsed_data.get('name', ''),
                    'domain': parsed_data.get('domain', '')
                })
        except Exception as e:
            print(f"Processing Error: {str(e)}")
            continue
            
    return results

def main():
    try:
        # Start with login
        driver = login_to_linkedin()
            
        current_page = 1
        max_pages = 100  # LinkedIn shows max 100 pages
        
        while current_page <= max_pages:
            # URLs for recruiters and managers
            urls = [
                f"https://www.linkedin.com/search/results/people/?industry=%5B%2296%22%5D&keywords=recruiter&origin=FACETED_SEARCH&page={current_page}",
                f"https://www.linkedin.com/search/results/people/?industry=%5B%2296%22%2C%221594%22%2C%226%22%5D&keywords=manager&origin=FACETED_SEARCH&page={current_page}"
            ]
            
            for url in urls:
                # Check if we've already reached max contacts
                if TOTAL_PROCESSED >= MAX_CONTACTS:
                    break
                    
                driver.get(url)
                
                # Wait for results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
                )
                
                # Let the page fully load
                time.sleep(3)
                
                # Get page source and process results
                results = process_linkedin_results(driver.page_source)
                global TOTAL_PROCESSED
                
                for person in results:
                    # Skip if we haven't reached minimum contacts
                    if TOTAL_PROCESSED < MIN_CONTACTS:
                        TOTAL_PROCESSED += 1
                        continue
                        
                    # Stop if we've reached maximum contacts
                    if TOTAL_PROCESSED >= MAX_CONTACTS:
                        print(f"Reached maximum number of contacts ({MAX_CONTACTS})")
                        return
                    
                    name = person['name']
                    company = person['domain']
                    
                    # Skip if already processed
                    if contact_exists(name):
                        print(f"Skipping {name} - already processed")
                        continue
                    
                    print(f"Processing {name} from {company} (Contact {TOTAL_PROCESSED + 1} of {MAX_CONTACTS})")
                    
                    # Get email
                    email = get_email(name, company)
                    
                    if email:
                        print(f"Found email for {name}: {email}")
                        if send_email(email, "Quick Chat?", name):
                            print(f"Email sent successfully to {name} at {email}")
                        else:
                            print(f"Failed to send email to {name} at {email}")
                    else:
                        print(f"No email found for {name}")
                    
                    # Save to database
                    save_contact(name, bool(email), email)
                    
                    # Increment processed count
                    TOTAL_PROCESSED += 1
                    
                    # Sleep to avoid rate limiting
                    time.sleep(2)
            
            # Check if we've reached max contacts before moving to next page
            if TOTAL_PROCESSED >= MAX_CONTACTS:
                print(f"Reached maximum number of contacts ({MAX_CONTACTS}). Stopping search.")
                break
                
            current_page += 1
            
            # Clean up old records
            cleanup_old_records()
            
            # Sleep between pages
            time.sleep(5)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
