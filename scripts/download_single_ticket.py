import requests
import json
import csv
from bs4 import BeautifulSoup

# Replace with your Freshdesk API Key and Domain
API_KEY = "FLn7Mbql5u5Q7HXScIzQ"
DOMAIN = "hyperverge.freshdesk.com"

# Replace with the specific ticket ID you want to fetch
TICKET_ID = 27401  

url = f"https://{DOMAIN}/api/v2/tickets/{TICKET_ID}"

# Make the API request
response = requests.get(url, auth=(API_KEY, "X"))

# Process the response
if response.status_code == 200:
    ticket = response.json()
    description = ticket.get('description', '')  # Get the description field
    
    # Parse the description to find image src
    soup = BeautifulSoup(description, 'html.parser')
    img_tags = soup.find_all('img')
    
    # Extract plain text version of the description
    description_txt = soup.get_text()

    # Print both descriptions to console
    print("HTML Description:")
    print(description)
    print("\nPlain Text Description:")
    print(description_txt)

    # Prepare ticket data for CSV
    ticket_data = {
        "Ticket ID": ticket.get("id"),
        "Subject": ticket.get("subject"),
        "Description": description,
        "Description Text": description_txt  # Save the plain text description
    }

    # Define CSV file path
    csv_filename = "ticket_details.csv"
    
    # Write to CSV
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Ticket ID", "Subject", "Description", "Description Text", "Image Source"])
        
        # Write header only if the file is empty
        file.seek(0, 2)  # Move to the end of the file to check if it's empty
        if file.tell() == 0:
            writer.writeheader()
        
        # Write the ticket data (without image sources)
        writer.writerow(ticket_data)
        
        # Write image sources in separate rows for each src
        for img in img_tags:
            img_src = img.get('src')
            img_data = ticket_data.copy()  # Copy existing ticket data
            img_data["Image Source"] = img_src  # Add image source
            writer.writerow(img_data)  # Write row with image source
    
    print(f"\nTicket details and image sources exported to {csv_filename}")
else:
    print(f"Error: {response.status_code}, {response.text}")