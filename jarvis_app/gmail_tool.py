import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from .google_auth import get_google_credentials
import logging

logger = logging.getLogger(__name__)


def get_gmail_service():
    """Initialize Gmail service"""
    creds = get_google_credentials()
    return build('gmail', 'v1', credentials=creds)


def read_emails(max_results=5, query='is:unread'):
    """Read emails from Gmail"""
    try:
        service = get_gmail_service()
        results = service.users().messages().list(
            userId='me', q=query, maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        if not messages:
            return {
                "status": "success",
                "emails": [],
                "message": "कोई ईमेल नहीं मिला | No emails found"
            }

        emails = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()

            headers = msg_data['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            # Extract body
            body = ''
            payload = msg_data['payload']
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')[:500]
                            break
            elif 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')[:500]

            emails.append({
                'id': msg['id'],
                'subject': subject,
                'from': sender,
                'date': date,
                'body_preview': body[:200],
            })

        return {
            "status": "success",
            "emails": emails,
            "count": len(emails),
            "message": f"{len(emails)} ईमेल मिले | Found {len(emails)} emails"
        }

    except Exception as e:
        logger.error(f"Gmail read error: {str(e)}")
        return {"status": "error", "message": f"Error reading emails: {str(e)}"}


def send_email(to: str, subject: str, body: str):
    """Send email via Gmail"""
    try:
        service = get_gmail_service()

        message = MIMEText(body, 'plain')
        message['to'] = to
        message['subject'] = subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()

        return {
            "status": "success",
            "message": f"✓ ईमेल भेजा गया {to} को | Email sent to {to}"
        }

    except Exception as e:
        logger.error(f"Gmail send error: {str(e)}")
        return {"status": "error", "message": f"Error sending email: {str(e)}"}


def search_emails(query: str, max_results=5):
    """Search emails with custom query"""
    return read_emails(max_results=max_results, query=query)


def mark_as_read(email_id: str):
    """Mark email as read"""
    try:
        service = get_gmail_service()
        service.users().messages().modify(
            userId='me', id=email_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return {"status": "success", "message": "✓ ईमेल पढ़ा गया के रूप में चिह्नित | Email marked as read"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_email(email_id: str):
    """Delete email"""
    try:
        service = get_gmail_service()
        service.users().messages().trash(userId='me', id=email_id).execute()
        return {"status": "success", "message": "✓ ईमेल हटाया गया | Email deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
