import requests
import json
import boto3
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree, tostring

aws_access_key = os.environ['aws_access_key']
aws_secret_key = os.environ['aws_secret_key']
bucket_name = os.environ['bucket_name']

# Initialize an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

blog_url = os.environ['blog_url']
circle_token = os.environ['circle_token']

payload = {}
headers = {'Authorization': f"{circle_token}"}

response = requests.request("GET", blog_url, headers=headers, data=payload)

if response.status_code == 200 and 'application/json' in response.headers.get('content-type', '').lower():
    # Parse the JSON data
    parsed_response = json.loads(response.text)

    # Create an RSS feed as an ElementTree
    rss = Element('rss', attrib={'version': '2.0'})
    channel = SubElement(rss, 'channel')
    title = SubElement(channel, 'title')
    title.text = "Opus Literary Alliance Community Blog"
    link = SubElement(channel, 'link')
    link.text = "https://olacirclerss.s3.us-east-2.amazonaws.com/rss.xml"
    description = SubElement(channel, 'description')
    description.text = "Your OLA Community Blog RSS Feed"

    for post in parsed_response:
        item = SubElement(channel, 'item')
        item_title = SubElement(item, 'title')
        item_title.text = post['name']
        item_link = SubElement(item, 'link')
        item_link.text = post['url']
        item_author = SubElement(item, 'author')
        item_author.text = post['user_name']
        item_published = SubElement(item, 'published_date')
        item_published.text = post['published_at']

    # Create an ElementTree object from the constructed XML
    rss_tree = ElementTree(rss)

    # Save the RSS feed to a file
    rss_feed_path = '/tmp/rss.xml'
    rss_tree.write(rss_feed_path, encoding='utf-8', xml_declaration=True)

    # Upload the RSS feed to S3
    s3.upload_file(rss_feed_path, bucket_name, 'rss.xml', ExtraArgs={'ACL': 'public-read'})
    # Print the RSS feed (for debugging)
    print(tostring(rss_tree.getroot(), encoding='utf-8').decode('utf-8'))
else:
    print(response.text)  # If not JSON, print the response as-is
