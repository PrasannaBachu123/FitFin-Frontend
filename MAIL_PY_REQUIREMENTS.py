"""
mail.py - Python Script Requirements for FitFin Email Integration

This document outlines the requirements for the mail.py script to work
with the FitFin email expense integration.

============================================
COMMAND LINE INTERFACE
============================================

The script MUST accept these command-line arguments:

1. --noe <count>     : Number of emails to fetch (1-50)
2. --debit           : Fetch debit transactions (expenses)
3. --credit          : Fetch credit transactions (income)

Example usage:
    python3 mail.py --noe 10 --credit
    python3 mail.py --noe 5 --debit

============================================
OUTPUT FORMAT
============================================

The script MUST output a JSON array to stdout with this exact structure:

[
  {
    "creditor": "Merchant or Sender Name",
    "amount": "500.00",
    "date": "20-01-26",
    "utr": "224860703XXX"
  },
  {
    "creditor": "Another Merchant",
    "amount": "1500.50",
    "date": "19-01-26",
    "utr": "123456789XXX"
  }
]

Field Requirements:
- creditor: String, merchant/sender name (required)
- amount: String or Number, transaction amount (required)
- date: String in DD-MM-YY format (required)
- utr: String, transaction reference number (optional but recommended)

============================================
ENVIRONMENT VARIABLES
============================================

The script MUST read Gmail credentials from environment variables:

Required:
- GMAIL_USER          : Gmail email address
- GMAIL_APP_PASSWORD  : Gmail App Password (16 characters, no spaces)

Optional:
- MAIL_SEARCH_DAYS    : Number of days to search back (default: 30)
- MAIL_MAX_RESULTS    : Maximum emails to process (default: 100)

============================================
ERROR HANDLING
============================================

1. Authentication Errors:
   - Exit with code 1
   - Print error to stderr (not stdout)
   - Example: "Authentication failed: Invalid credentials"

2. No Emails Found:
   - Output empty array: []
   - Exit with code 0

3. Parsing Errors:
   - Skip invalid emails
   - Continue processing valid ones
   - Log errors to stderr

4. Rate Limiting:
   - Implement exponential backoff
   - Exit with code 2 if rate limit exceeded

============================================
EXAMPLE IMPLEMENTATION STRUCTURE
============================================
"""

#!/usr/bin/env python3
import os
import sys
import json
import argparse
import imaplib
import email
from datetime import datetime, timedelta

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Fetch expenses from Gmail')
    parser.add_argument('--noe', type=int, required=True,
                        help='Number of emails to fetch (1-50)')
    parser.add_argument('--debit', action='store_true',
                        help='Fetch debit transactions')
    parser.add_argument('--credit', action='store_true',
                        help='Fetch credit transactions')
    return parser.parse_args()

def validate_arguments(args):
    """Validate command line arguments"""
    if args.noe < 1 or args.noe > 50:
        print("Error: Email count must be between 1 and 50", file=sys.stderr)
        sys.exit(1)

    if not (args.debit or args.credit):
        print("Error: Must specify either --debit or --credit", file=sys.stderr)
        sys.exit(1)

    if args.debit and args.credit:
        print("Error: Cannot specify both --debit and --credit", file=sys.stderr)
        sys.exit(1)

def get_gmail_credentials():
    """Get Gmail credentials from environment"""
    gmail_user = os.getenv('GMAIL_USER')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')

    if not gmail_user or not gmail_password:
        print("Error: GMAIL_USER and GMAIL_APP_PASSWORD must be set", file=sys.stderr)
        sys.exit(1)

    return gmail_user, gmail_password

def connect_to_gmail(gmail_user, gmail_password):
    """Connect to Gmail via IMAP"""
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(gmail_user, gmail_password)
        return mail
    except imaplib.IMAP4.error as e:
        print(f"Error: Authentication failed - {str(e)}", file=sys.stderr)
        sys.exit(1)

def search_emails(mail, transaction_type, count):
    """Search for transaction emails"""
    mail.select('inbox')

    # Build search query based on transaction type
    # Customize these keywords based on your bank's email format
    if transaction_type == 'debit':
        search_query = '(OR SUBJECT "debited" SUBJECT "spent" SUBJECT "payment made")'
    else:  # credit
        search_query = '(OR SUBJECT "credited" SUBJECT "received" SUBJECT "payment received")'

    # Search for emails from last 30 days
    date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
    search_query = f'(SINCE {date} {search_query})'

    status, messages = mail.search(None, search_query)
    email_ids = messages[0].split()

    # Get latest N emails
    return email_ids[-count:] if len(email_ids) > count else email_ids

def parse_transaction_email(email_message):
    """
    Parse email to extract transaction details

    Customize this function based on your bank's email format
    """
    subject = email_message.get('subject', '')
    body = ''

    # Get email body
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = email_message.get_payload(decode=True).decode()

    # Example parsing logic - CUSTOMIZE THIS FOR YOUR BANK
    # This is a placeholder - implement actual parsing based on email format
    transaction = {
        "creditor": "Unknown Merchant",  # Parse from email
        "amount": "0.00",                # Parse from email
        "date": datetime.now().strftime("%d-%m-%y"),  # Parse from email
        "utr": "N/A"                     # Parse from email
    }

    # TODO: Implement actual parsing logic here
    # Example regex patterns:
    # - Amount: r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
    # - UTR: r'UTR[:\s]+(\d+)'
    # - Date: r'(\d{2})[/-](\d{2})[/-](\d{2,4})'
    # - Merchant: r'to\s+([A-Z\s]+)'

    return transaction

def fetch_transactions(args):
    """Main function to fetch transactions"""
    # Get credentials
    gmail_user, gmail_password = get_gmail_credentials()

    # Connect to Gmail
    mail = connect_to_gmail(gmail_user, gmail_password)

    # Determine transaction type
    transaction_type = 'debit' if args.debit else 'credit'

    # Search for emails
    email_ids = search_emails(mail, transaction_type, args.noe)

    transactions = []

    # Parse each email
    for email_id in email_ids:
        try:
            _, msg_data = mail.fetch(email_id, '(RFC822)')
            email_message = email.message_from_bytes(msg_data[0][1])

            transaction = parse_transaction_email(email_message)
            transactions.append(transaction)

        except Exception as e:
            print(f"Warning: Failed to parse email {email_id}: {str(e)}",
                  file=sys.stderr)
            continue

    # Close connection
    mail.close()
    mail.logout()

    return transactions

def main():
    """Main entry point"""
    try:
        # Parse and validate arguments
        args = parse_arguments()
        validate_arguments(args)

        # Fetch transactions
        transactions = fetch_transactions(args)

        # Output JSON to stdout
        print(json.dumps(transactions, indent=2))

        # Exit successfully
        sys.exit(0)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

"""
============================================
TESTING CHECKLIST
============================================

1. Test with valid credentials:
   python3 mail.py --noe 5 --credit

2. Test with invalid credentials:
   GMAIL_USER=wrong@email.com python3 mail.py --noe 5 --credit
   (Should exit with error)

3. Test output is valid JSON:
   python3 mail.py --noe 5 --debit | python3 -m json.tool

4. Test with no emails found:
   (Should output empty array [])

5. Test edge cases:
   python3 mail.py --noe 1 --credit   # Minimum
   python3 mail.py --noe 50 --debit   # Maximum
   python3 mail.py --noe 0 --credit   # Invalid (should error)
   python3 mail.py --noe 51 --credit  # Invalid (should error)

6. Verify no print statements except final JSON

7. Verify errors go to stderr, not stdout

============================================
BANK-SPECIFIC CUSTOMIZATION
============================================

The parse_transaction_email() function needs to be customized
based on your bank's email format. Common patterns:

HDFC Bank:
- Subject: "Your Account XX1234 has been debited"
- Amount in: "INR 1,234.56"
- UTR in: "UTR No. 123456789012"

ICICI Bank:
- Subject: "ICICI Bank Acct XX1234 debited"
- Amount in: "Rs. 1234.56"
- Reference: "Ref no 123456789"

SBI:
- Subject: "Alert: Your Acct XX1234 debited"
- Amount in: "INR 1,234.56"
- UTR: "IMPS Ref No: 123456789"

Axis Bank:
- Subject: "Your Account XX1234 is debited"
- Amount in: "Rs 1234.56"
- Reference: "Txn ID: 123456789"

Example regex for amount extraction:
    import re
    amount_match = re.search(r'(?:Rs\.?|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)', body)
    if amount_match:
        amount = amount_match.group(1).replace(',', '')

============================================
DEPENDENCIES
============================================

Required Python packages:
- Standard library only (no external dependencies)
- imaplib (built-in)
- email (built-in)
- json (built-in)
- argparse (built-in)

Optional for better parsing:
- pip install beautifulsoup4  # For HTML emails
- pip install python-dateutil # For date parsing

============================================
PERFORMANCE CONSIDERATIONS
============================================

1. Limit email search to recent dates (last 30 days)
2. Use IMAP search queries to filter on server
3. Cache parsed emails to avoid re-fetching
4. Implement connection pooling for multiple requests
5. Add timeout for IMAP operations
6. Handle large email bodies efficiently

============================================
SECURITY BEST PRACTICES
============================================

1. Never log or print Gmail credentials
2. Use App Password, never regular password
3. Clear credentials from memory after use
4. Implement rate limiting (max 10 requests/hour)
5. Validate all inputs before processing
6. Sanitize output to prevent injection attacks
7. Use TLS/SSL for all connections
8. Store credentials in environment, never in code

============================================
"""
