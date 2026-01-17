from datetime import datetime
from googleapiclient.discovery import build
import pickle 

# Init google calendar service
with open('token.pkl', 'rb') as token_file:
    creds = pickle.load(token_file)

service = build('calendar', 'v3', credentials=creds)

def delete_events_in_range(service, calendar_id='primary', start_date_str="2029-10-14", end_date_str="2029-10-20"):
    # Convert strings to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    # Build proper RFC3339 strings
    start_rfc3339 = start_date.replace(hour=0, minute=0, second=0).isoformat() + "+08:00"
    end_rfc3339   = end_date.replace(hour=23, minute=59, second=59).isoformat() + "+08:00"
    
    # Fetch events in range
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_rfc3339,
        timeMax=end_rfc3339,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    print(f"Found {len(events)} events to delete.")
    
    # Delete each event
    for event in events:
        service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
        print(f"Deleted event: {event.get('summary')}")

def delete_calendar(service, calendar_id):
    if calendar_id == 'primary':
        raise ValueError("Cannot delete the primary calendar. Use a secondary calendar ID.")
    
    try:
        # Single API call to delete the entire calendar
        service.calendars().delete(calendarId=calendar_id).execute()
        print(f"✓ Calendar '{calendar_id}' has been deleted successfully.")
        print("  All events within it were automatically removed.")
        return True
    except Exception as e:
        print(f"✗ Error deleting calendar: {e}")
        return False

def list_calendars(service):
    calendar_list = service.calendarList().list().execute()
    
    calendars = {}
    for calendar in calendar_list['items']:
        calendars[calendar['summary']] = {
            'id': calendar['id'],
            'primary': calendar.get('primary', False)
        }
    
    return calendars

def create_calendar(service, title):
    calendar = {
        'summary': title,
        'timeZone': 'Asia/Singapore'
    }
    
    created_calendar = service.calendars().insert(body=calendar).execute()
    
    print(f"Calendar created: {created_calendar['summary']}")
    print(f"Calendar ID: {created_calendar['id']}")
    
    return created_calendar['id']

def get_calendar_ids(service):
    calendars = list_calendars(service)
    result = []

    for i in range(6):
        if str(i) not in calendars:
            print(f"Calendar {i} not exists")
            id = create_calendar(service, str(i))
            result.append(id)
        else:
            result.append(calendars[str(i)]["id"])
    return result

calendars = get_calendar_ids(service)
for i in range(6):
    delete_calendar(service, calendars[i])