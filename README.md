# AI-Powered LinkedIn Outreach Assistant

This Python project leverages advanced AI technologies to intelligently automate LinkedIn prospecting and personalized email outreach. Using the Mistral-7B Large Language Model, it analyzes LinkedIn profiles, extracts relevant information, and generates contextually appropriate outreach messages.

## Features

- Advanced AI profile analysis using Mistral-7B LLM
- Intelligent contact information extraction with deep learning
- Smart LinkedIn profile scraping with Selenium
- Email discovery using GetProspect API
- Automated personalized email sending
- MongoDB database for tracking contacts
- Rate limiting and pagination handling
- AI-powered contact information extraction

## Setup

1. Create a virtual environment and activate it:
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Copy sample.env to .env and update with your credentials:
```powershell
Copy-Item sample.env .env
```

4. Update the email template in `email_template.txt` with your message

## Configuration

Update the `.env` file with your:
- SMTP email server details
- GetProspect API key
- MongoDB password
- Hugging Face API key for Mistral-7B

## Usage

Run the main script:
```powershell
python linkedin_scraper.py
```

The script will:
1. Search LinkedIn for recruiters and managers
2. Find their email addresses
3. Send personalized emails
4. Track all interactions in MongoDB

## Safety Features

- Rate limiting to avoid API blocks
- Database tracking to prevent duplicate emails
- Automatic cleanup of old records
- Error handling and logging

## Note

Please ensure you comply with LinkedIn's terms of service and relevant privacy laws when using this tool.
