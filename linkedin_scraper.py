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
import os
from dotenv import load_dotenv

load_dotenv()

def setup_driver():
    chrome_options = Options()
    # Add options for headless mode if needed
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_domain_from_company(company):
    """
    Extract domain from company name
    You might want to enhance this with a company domain lookup service
    """
    # Remove common suffixes and convert to lowercase
    company = company.lower().replace(' at ', '').replace('ltd', '').replace('inc', '').strip()
    # Convert to domain format
    domain = f"{company.replace(' ', '')}.com"
    return domain

def process_linkedin_results(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []
    
    # Adjust these selectors based on the actual LinkedIn HTML structure
    person_cards = soup.find_all('div', class_='entity-result__item')
    
    for card in person_cards:
        try:
            name = card.find('span', class_='entity-result__title-text').get_text().strip()
            company = card.find('div', class_='entity-result__primary-subtitle').get_text().strip()
            
            results.append({
                'name': name,
                'company': company
            })
        except:
            continue
            
    return results

def main():
    driver = setup_driver()
    current_page = 1
    max_pages = 100  # LinkedIn shows max 100 pages
    
    try:
        # Get the email template
        with open('email_template.txt', 'r') as f:
            email_template = f.read()
        
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
                    
                    # Get company domain
                    domain = extract_domain_from_company(company)
                    
                    # Get email
                    email = get_email(name, domain)
                    
                    if email:
                        # Send email
                        if send_email(email, "Opportunity to Connect", email_template, name):
                            print(f"Email sent successfully to {name} at {email}")
                        else:
                            print(f"Failed to send email to {name} at {email}")
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
