import re
import csv
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
from dateutil import parser
import subprocess

# Set up the calendar service using OAuth 2.0
def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    return service

# Prompt for input on past/future and day range
def get_user_input():
    while True:
        direction = input("Do you want events from 'past' or 'future'? ").strip().lower()
        if direction not in ["past", "future"]:
            print("Invalid input. Please type 'past' or 'future'.")
            continue
        
        try:
            days = int(input(f"Enter the number of days for {direction} events: "))
            if days < 1:
                print("Please enter a positive integer for days.")
                continue
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue
        return direction, days

# Calculate date range for the specified direction and days
def get_date_range(direction, days):
    # Use UTC time with correct timezone information
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    
    if direction == "past":
        start_time = (now - datetime.timedelta(days=days)).isoformat()
        end_time = now.isoformat()
    else:
        start_time = now.isoformat()
        end_time = (now + datetime.timedelta(days=days)).isoformat()
    
    print(f"Date range: Start={start_time}, End={end_time}")  # Debugging line
    return start_time, end_time


# Fetch events based on the date range with added debugging
def fetch_events(service, start_time, end_time):
    print(f"Fetching events from {start_time} to {end_time}")
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time,
        timeMax=end_time,
        maxResults=500,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Debugging: Print number of events retrieved
    print(f"Number of events fetched: {len(events)}")
    
    if not events:
        print("No events found in the specified range.")
        return []

    all_events = []
    for event in events:
        summary = event.get("summary", "No Title")
        start = event.get("start", {}).get("dateTime", "No Start Time")
        end = event.get("end", {}).get("dateTime", "No End Time")

        print(f"Event: {summary}, Start: {start}, End: {end}")
        
        if start != "No Start Time" and end != "No End Time":
            try:
                start_time = parser.parse(start)
                end_time = parser.parse(end)
                duration = (end_time - start_time).total_seconds() / 3600
            except ValueError:
                duration = "Unknown"
        else:
            duration = "Unknown"

        event_info = {
            "summary": summary,
            "start": start,
            "end": end,
            "duration_hours": duration
        }
        all_events.append(event_info)
    
    all_events.sort(key=lambda x: x["start"])
    return all_events

# Function to segregate events based on numeric category
def segregate_events(events):
    categorized_events = {}
    for event in events:
        # Extract starting number using regular expression
        match = re.match(r"^(\d+)", event["summary"])
        if match:
            category = int(match.group(1))
            if category not in categorized_events:
                categorized_events[category] = []
            categorized_events[category].append(event)
    return categorized_events

# Save segregated events to CSV files by category
def save_categorized_events_to_csv(categorized_events, filename='categorized_calendar_events.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Category", "Summary", "Start", "End", "Duration (hours)"])
        
        for category, events in categorized_events.items():
            for event in events:
                writer.writerow([category, event["summary"], event["start"], event["end"], event["duration_hours"]])
    print(f"Categorized events saved to {filename}")

# Main function to run the script
if __name__ == '__main__':
    service = get_calendar_service()
    direction, days = get_user_input()
    start_time, end_time = get_date_range(direction, days)
    events = fetch_events(service, start_time, end_time)
    
    # Save sorted events to CSV, overwriting any previous data
    if events:
        categorized_events = segregate_events(events)
        save_categorized_events_to_csv(categorized_events)
        
        # Automatically run visualization.py to update the HTML visualization
        print("Generating updated visualization in HTML...")
        subprocess.run(["python", "visualization.py"])