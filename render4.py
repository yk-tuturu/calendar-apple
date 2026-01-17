import pickle
from googleapiclient.discovery import build
import cv2
import numpy as np
from datetime import datetime, timedelta
import os

def create_event(base_date, row, col, slot_length, service, calendar_id, tz_offset="+08:00"):
    # Calculate start and end datetime
    start_dt = base_date + timedelta(days=col, hours=row)
    end_dt = start_dt + timedelta(hours=slot_length)

    if slot_length == 24:
        end_dt = end_dt - timedelta(minutes=1)
    
    # Convert to RFC3339 format
    start_str = start_dt.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}")
    end_str = end_dt.strftime(f"%Y-%m-%dT%H:%M:%S{tz_offset}")
    
    # Event dictionary
    event = {
        'summary': 'bad apple',  # Pixel
        'description': 'This is a test event added from Python.',
        'start': {'dateTime': start_str, 'timeZone': 'Asia/Singapore'},
        'end': {'dateTime': end_str, 'timeZone': 'Asia/Singapore'}
    }
    
    # Insert event
    service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Created event from {start_dt} to {end_dt} in calendar id: {calendar_id}")

def render_frame(service, filepath, base_date, calendars):
    frame = cv2.imread(filepath, 0) # read image as grayscale. Set second parameter to 1 if rgb is required

    calendar_frame = cv2.resize(
        frame.astype(np.uint8),       # must be uint8 for cv2
        (14, 48),                      # width x height
        interpolation=cv2.INTER_AREA  # good for downscaling
    )

    calendar_frame = (calendar_frame / 255.0 > 0.5).astype(int)

    grid_positions = [
        (0, 23, 0, 6),    
        (0, 23, 7, 13),   
        (24, 47, 0, 6),   
        (24, 47, 7, 13),
    ]

    for calendar_idx in range(4):
        calendar_id = calendars[calendar_idx]
        row_start, row_end, col_start, col_end = grid_positions[calendar_idx]

        for col in range(7):
            curr_length = 0
            curr_start = 0
            gathering = False
            for row in range(24):
                pixel = calendar_frame[row_start + row, col_start + col]
                if pixel == 1:
                    if not gathering: 
                        curr_start = row
                        curr_length = 1
                        gathering = True
                    else:
                        curr_length += 1
                
                else:
                    # end of a block
                    if gathering:
                        create_event(base_date, curr_start, col, curr_length, service, calendar_id)
                        gathering = False
                        curr_length = 0
            
            if gathering:
                create_event(base_date, curr_start, col, curr_length, service, calendar_id)
    
    print(f"Rendered frame: {filepath}")

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

    for i in range(4):
        if str(i) not in calendars:
            print(f"Calendar {i} not exists")
            id = create_calendar(service, str(i))
            result.append(id)
        else:
            result.append(calendars[str(i)]["id"])
    return result

def render_all():
    curr = 0
    limit = 50
    directory = "frames"
    base_date = datetime.strptime("2026-01-18", "%Y-%m-%d")

    # Init google calendar service
    with open('token.pkl', 'rb') as token_file:
        creds = pickle.load(token_file)

    service = build('calendar', 'v3', credentials=creds)

    calendars = get_calendar_ids(service)
    # render_frame(service, "frames/frame_0207.png", base_date, calendars)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath) and filepath.lower().endswith(".png"):
            render_frame(service, filepath, base_date, calendars)
            curr += 1
            base_date += timedelta(days=7)

    print("Done")

render_all()

            