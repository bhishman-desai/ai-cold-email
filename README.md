# LinkedIn Cold Email Automation

This Python project automates the process of finding and reaching out to potential LinkedIn connections via email.

## Features

- LinkedIn profile scraping
- Email discovery using getemail.io
- Automated email sending
- SQLite database for tracking contacts
- Rate limiting and pagination handling

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
- LinkedIn credentials
- SMTP email server details
- getemail.io API key

## Usage

Run the main script:
```powershell
python linkedin_scraper.py
```

The script will:
1. Search LinkedIn for recruiters and managers
2. Find their email addresses
3. Send personalized emails
4. Track all interactions in the SQLite database

## Safety Features

- Rate limiting to avoid API blocks
- Database tracking to prevent duplicate emails
- Automatic cleanup of old records
- Error handling and logging

## Note

Please ensure you comply with LinkedIn's terms of service and relevant privacy laws when using this tool.
