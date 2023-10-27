import asyncio
import feedparser
import aiohttp
import requests
import os
import configparser

FEED_URLS = {
    "https://example.feed.com/feed": "member_author@email.com",
    "https://example2.feed.com/feed/": "member_author2@email.com"
    # Add more mappings as needed
}


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
        space_id = config['Credentials']['space_id']
    except KeyError as e:
        print(f"Key not found in the config file: {e}")
    except configparser.NoSectionError as e:
        print(f"Section not found in the config file: {e}")
else:
    circle_token = os.environ['circle_token']
    community_id = os.environ['community_id']
    space_id = os.environ['space_id']


async def fetch_feed(url, session):
    async with session.get(url) as response:
        content = await response.text()
        return feedparser.parse(content)


async def fetch_latest_post(url, user_email, session):
    feed = await fetch_feed(url, session)
    if not feed.entries:
        return {"error": "No items found in RSS feed."}

    latest_post = feed.entries[0]
    description = latest_post.summary if 'summary' in latest_post else "No description available"
    max_length = 200
    if len(description) > max_length:
        description = description[:max_length] + '...'

    return {
        "date": latest_post.published,
        "title": latest_post.title,
        "body": description,
        "url": latest_post.link,
        "user_email": user_email  # Adding user_email to the post data
    }


async def fetch_existing_posts(session, community_id, space_id):
    url = f"https://app.circle.so/api/v1/posts?community_id={community_id}&space_id={space_id}"
    headers = {"Authorization": f"{circle_token}"}

    existing_posts = {}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            # Directly iterate over data if it's a list
            for post in data:  # Assuming the API directly returns a list of posts
                existing_posts[post.get("name")] = post.get("id")
        else:
            print("Failed to fetch existing posts: ", response.status)
            return existing_posts

    return existing_posts


def post_to_circle(post_data, user_email=None):
    # Extract necessary data from post_data
    title = post_data["title"]
    body = post_data["body"]
    original_url = post_data["url"]  # URL from the RSS feed

    # Append the original post URL to the body
    body_with_url = f"{body}\n\nOriginal post: {original_url}"

    description = body_with_url  # Or however you want to set the description

    # Ensure the data is URL-encoded to handle special characters
    from urllib.parse import quote
    title_encoded = quote(title)
    body_encoded = quote(body_with_url)
    description_encoded = quote(description)

    # Construct the URL with the encoded data
    url = (f"https://app.circle.so/api/v1/posts?"
           f"community_id={community_id}&space_id={space_id}&"
           f"name={title_encoded}&body={body_encoded}&"
           f"is_pinned=false&is_comments_enabled=true&"
           f"is_comments_closed=false&is_liking_enabled=true&"
           f"skip_notifications=false&"
           f"meta_title={title_encoded}&meta_description={description_encoded}&"
           f"opengraph_title={title_encoded}&opengraph_description={description_encoded}&"
           f"hide_from_featured_areas=false")
    if user_email:
        url += f"&user_email={quote(user_email)}"
    headers = {
        "Authorization": f"{circle_token}"
    }

    # Make a POST request to create the post in Circle
    response = requests.post(url, headers=headers)
    return response.json()


async def fetch_all_feeds():
    async with aiohttp.ClientSession() as session:
        existing_posts = await fetch_existing_posts(session, community_id, space_id)

        tasks = [fetch_latest_post(url, email, session) for url, email in FEED_URLS.items()]
        all_posts = await asyncio.gather(*tasks)

        for post in all_posts:
            if "error" in post:
                continue

            # Check if post already exists
            if post["title"] in existing_posts:
                print(f"Post with title '{post['title']}' already exists. Skipping...")
                continue

            circle_response = post_to_circle(post, post['user_email'])
            print(circle_response)


asyncio.run(fetch_all_feeds())
