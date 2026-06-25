import pytz
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from .google_auth import get_google_credentials
import logging
import uuid

logger = logging.getLogger(__name__)
IST = pytz.timezone('Asia/Kolkata')


def get_calendar_service():
    creds = get_google_credentials()
    return build('calendar', 'v3', credentials=creds)


def list_events(days_ahead=7):
    try:
        service = get_calendar_service()
        
        # ✅ IST-aware now
        now = datetime.now(IST).isoformat()
        time_max = (datetime.now(IST) + timedelta(days=days_ahead)).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=time_max,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return {
                "status": "success",
                "events": [],
                "message": f"अगले {days_ahead} दिनों में कोई ईवेंट नहीं | No events in next {days_ahead} days"
            }

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            meet_link = event.get('hangoutLink', '')
            
            event_list.append({
                'id': event['id'],
                'title': event['summary'],
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'meet_link': meet_link,  # ✅ Meet link include
            })

        return {
            "status": "success",
            "events": event_list,
            "count": len(event_list),
            "message": f"{len(event_list)} इवेंट मिले | Found {len(event_list)} events"
        }

    except Exception as e:
        logger.error(f"Calendar list error: {str(e)}")
        return {"status": "error", "message": f"Error listing events: {str(e)}"}


def create_event(title: str, start_time: str, end_time: str, description: str = ""):
    try:
        service = get_calendar_service()

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
            # ✅ Google Meet auto-generate
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1  # ✅ Yeh zaroori hai Meet link ke liye
        ).execute()

        meet_link = created_event.get('hangoutLink', 'No Meet link generated')

        return {
            "status": "success",
            "event_id": created_event['id'],
            "meet_link": meet_link,  # ✅ Link return karo
            "message": f"✓ Event '{title}' created! Google Meet link: {meet_link}"
        }

    except Exception as e:
        logger.error(f"Calendar create error: {str(e)}")
        return {"status": "error", "message": f"Error creating event: {str(e)}"}


# ... baaki functions same rehenge (update_event, delete_event, search_events)
def update_event(event_id: str, title: str = None, start_time: str = None, end_time: str = None):
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

        if title:
            event['summary'] = title
        if start_time:
            event['start'] = {'dateTime': start_time, 'timeZone': 'Asia/Kolkata'}
        if end_time:
            event['end'] = {'dateTime': end_time, 'timeZone': 'Asia/Kolkata'}

        service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return {"status": "success", "message": "✓ Event updated successfully"}

    except Exception as e:
        logger.error(f"Calendar update error: {str(e)}")
        return {"status": "error", "message": f"Error updating event: {str(e)}"}


def delete_event(event_id: str):
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"status": "success", "message": "✓ Event deleted successfully"}
    except Exception as e:
        logger.error(f"Calendar delete error: {str(e)}")
        return {"status": "error", "message": f"Error deleting event: {str(e)}"}


def search_events(query: str):
    try:
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId='primary',
            q=query,
            maxResults=5,
            singleEvents=True,
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return {"status": "success", "events": [], "message": f"No events found for '{query}'"}

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_list.append({
                'id': event['id'],
                'title': event['summary'],
                'start': start,
                'end': end,
                'meet_link': event.get('hangoutLink', ''),
            })

        return {"status": "success", "events": event_list, "count": len(event_list)}

    except Exception as e:
        logger.error(f"Calendar search error: {str(e)}")
        return {"status": "error", "message": f"Error searching events: {str(e)}"}