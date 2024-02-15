import configparser
import os
import requests
import csv

# Path to the config file (Used for running the script locally instead of via Pipedream
config_file_path = os.path.expanduser('~/.ola/config.ini')

# Check if the file exists
if os.path.exists(config_file_path):
    # Initialize the configparser
    config = configparser.ConfigParser()
    # Read the config file
    config.read(config_file_path)

    try:
        circle_token = config['Credentials']['circle_token']
        community_id = config['Credentials']['community_id']
        learn_space_id = config['Credentials']['learn_space_id']
    except KeyError as e:
        print(f"Key not found in the config file: {e}")
    except configparser.NoSectionError as e:
        print(f"Section not found in the config file: {e}")
else:
    circle_token = os.environ['circle_token']
    community_id = os.environ['community_id']
    learn_space_id = os.environ['learn_space_id']

# Path to your CSV file with email addresses
csv_file_path = '/Users/darlabaker/.ola/emails.csv'

# Read email addresses from the CSV file
with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    member_emails_to_remove = [row[0] for row in reader]

# Circle API endpoint for removing a member from a space
remove_member_endpoint = f"https://app.circle.so/api/v1/space_members?space_id={learn_space_id}&community_id={community_id}&email="

# Headers for the API request
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'{circle_token}'
}

response = requests.request("DELETE", remove_member_endpoint, headers=headers)

print(response.text)
# Iterate over the member emails and remove each from the space
for member_email in member_emails_to_remove:
    response = requests.delete(f"{remove_member_endpoint}{member_email}", headers=headers)
    if response.status_code == 200:
        print(f"Successfully removed member {member_email} from space {learn_space_id}")
    else:
        print(f"Failed to remove member {member_email} from space {learn_space_id}. Status code: {response.status_code}, Response: {response.text}")
