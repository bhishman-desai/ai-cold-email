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

load_dotenv()

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

def process_linkedin_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # Find all person cards in the search results
    person_cards = soup.find_all('div', {'class': 'entity-result__item'})
    
    for card in person_cards:
        try:
            # Find the name element
            name_element = card.find('span', {'class': 'entity-result__title-text'})
            name = name_element.get_text().strip() if name_element else ''
            
            # Find the company element
            company_element = card.find('div', {'class': 'entity-result__primary-subtitle'})
            company = company_element.get_text().strip() if company_element else ''
            
            if name and company:
                # Clean up company name - remove "at" and other common words
                company = company.replace(' at ', ' ').replace(' @ ', ' ').strip()
                
                results.append({
                    'name': name,
                    'company': company
                })
        except Exception as e:
            print(f"Error processing card: {str(e)}")
            continue
            
    return results

def main():
    try:
        # Start with login
        driver = login_to_linkedin()
        
        # Get the email template
        with open('email_template.txt', 'r') as f:
            email_template = f.read()
            
        current_page = 1
        max_pages = 1  # LinkedIn shows max 100 pages
        
        while current_page <= max_pages:
            # URLs for recruiters and managers
            urls = [
                f"https://www.linkedin.com/search/results/people/?industry=%5B%2296%22%5D&keywords=recruiter&origin=FACETED_SEARCH&page={current_page}",
                f"https://www.linkedin.com/search/results/people/?industry=%5B%2296%22%2C%221594%22%2C%226%22%5D&keywords=manager&origin=FACETED_SEARCH&page={current_page}"
            ]
            
            for url in urls:
                driver.get(url)
                
                # Wait for results to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
                )
                
                # Let the page fully load
                time.sleep(3)
                
                # Get page source and process results
                results = process_linkedin_results(driver.page_source)
                
                for person in results:
                    name = person['name']
                    company = person['company']
                    
                    # Skip if already processed
                    if contact_exists(name):
                        print(f"Skipping {name} - already processed")
                        continue
                    
                    print(f"Processing {name} from {company}")
                    
                    # Get email
                    email = get_email(name, company)
                    
                    if email:
                        print(f"Found email for {name}: {email}")
                        # Uncomment the following lines when ready to send emails
                        # if send_email(email, "Opportunity to Connect", email_template, name):
                        #     print(f"Email sent successfully to {name} at {email}")
                        # else:
                        #     print(f"Failed to send email to {name} at {email}")
                    else:
                        print(f"No email found for {name}")
                    
                    # Save to database
                    save_contact(name, bool(email), email)
                    
                    # Sleep to avoid rate limiting
                    time.sleep(2)
            
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
