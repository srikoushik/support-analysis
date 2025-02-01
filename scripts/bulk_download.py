import requests
import json
import csv
import os
from bs4 import BeautifulSoup

# Replace with your Freshdesk API Key and Domain
API_KEY = "FLn7Mbql5u5Q7HXScIzQ" #"Vxv3ZV9BI6tsWc3i7"
DOMAIN = "hyperverge.freshdesk.com" #"autoassist.freshdesk.com"

# Define start and end date (Modify as needed)
START_DATE = "2025-01-01T00:00:00Z"  # Start date (YYYY-MM-DDTHH:MM:SSZ)
END_DATE = "2025-01-07T23:59:59Z"    # End date (YYYY-MM-DDTHH:MM:SSZ)

# Initialize variables
page = 1
all_tickets = []

# Function to extract image sources from the description
def extract_images_from_description(description):
    soup = BeautifulSoup(description, "html.parser")
    img_tags = soup.find_all("img")
    img_urls = [img.get("src") for img in img_tags if img.get("src")]
    return img_urls

# Loop through pages (handling pagination)
while True:
    url = f"https://{DOMAIN}/api/v2/tickets?updated_since={START_DATE}&page={page}&per_page=100"
    response = requests.get(url, auth=(API_KEY, "X"))

    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        break

    tickets = response.json()
    
    if not tickets:  # Stop when no more tickets
        break
    
    # Filter tickets within the END_DATE
    filtered_tickets = [t for t in tickets if t["updated_at"] <= END_DATE]

    # Fetch full details (including description and description_text) for each ticket
    for ticket in filtered_tickets:
        ticket_id = ticket["id"]
        ticket_url = f"https://{DOMAIN}/api/v2/tickets/{ticket_id}"
        ticket_response = requests.get(ticket_url, auth=(API_KEY, "X"))

        if ticket_response.status_code == 200:
            full_ticket = ticket_response.json()
            ticket["description"] = full_ticket.get("description", "No Description Available")
            ticket["description_text"] = full_ticket.get("description_text", "No Description Text Available")

            # Extract image URLs from description
            img_urls = extract_images_from_description(ticket["description"])

            # Append the image URLs to the ticket
            ticket["image_urls"] = ", ".join(img_urls) if img_urls else "No Images"
        else:
            ticket["description"] = "Failed to fetch description"
            ticket["description_text"] = "Failed to fetch description text"
            ticket["image_urls"] = "Failed to fetch images"

    all_tickets.extend(filtered_tickets)
    page += 1  # Move to next page

print(f"Total tickets retrieved: {len(all_tickets)}")

# Save tickets as JSON
with open("filtered_tickets_with_description_and_images.json", "w", encoding="utf-8") as file:
    json.dump(all_tickets, file, indent=4)

# Save tickets as CSV
with open("tickets_filtered_with_description_and_images.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["ID", "Subject", "Status", "Priority", "Updated At", "Description", "Description Text", "Image URLs"])  # Headers
    
    for ticket in all_tickets:
        writer.writerow([
            ticket["id"], 
            ticket["subject"], 
            ticket["status"], 
            ticket["priority"], 
            ticket["updated_at"], 
            ticket["description"],
            ticket["description_text"],
            ticket["image_urls"]
        ])

print("Tickets with descriptions, description_text, and images saved successfully.")