import configparser
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

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
        publisher_space_id = config['Credentials']['publisher_space_id']
        author_space_id = config['Credentials']['author_space_id']
        endpoint_url = config['URLs']['endpoint_url']
    except KeyError as e:
        print(f"Key not found in the config file: {e}")
    except configparser.NoSectionError as e:
        print(f"Section not found in the config file: {e}")
else:
    circle_token = os.environ['circle_token']
    community_id = os.environ['community_id']
    publisher_space_id = os.environ['publisher_space_id']
    author_space_id = os.environ['author_space_id']


def handler(pd):
    try:
        # Try to access the Pipedream data
        user_email = pd.steps["trigger"]["event"]["query"]["user_email"]
        user_type = pd.steps["trigger"]["event"]["query"]["user_type"]
        book_link = pd.steps["trigger"]["event"]["query"]["book_link"]
    except AttributeError:
        # If not running in Pipedream, set default values
        user_email = "darla.baker@bakewell.me"
        user_type = "author"
        book_link = "https://www.amazon.com/Eagle-Cove-Thalia-Chase-Therapist-ebook/dp/B01EQL8HYY/"

    # Set space_id based on user_type
    if user_type.lower() == "author":
        space_id = author_space_id  # Ensure this variable is defined somewhere
    elif user_type.lower() == "publisher":
        space_id = publisher_space_id  # Ensure this variable is defined somewhere
    else:
        space_id = author_space_id  # Default case

    # Return all the variables
    return user_email, user_type, book_link, space_id


user_email, user_type, book_link, space_id = handler(None)
print("Space ID:", space_id)
print("User Email:", user_email)
print("Book Link", book_link)


def get_book_details(url):
    # Set up the Selenium Chrome driver options
    chrome_driver_path = '/Users/darlabaker/Desktop/Dropbox/repositories/CircleRSS/chromedriver'
    options = Options()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/92.0.4515.131 Safari/537.36")
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU acceleration for headless mode
    # options.add_experimental_option("detach", True)
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    try:
        driver.get(url)
        time.sleep(10)  # Adjust the sleep time as necessary

        title_element = driver.find_element(By.ID, "productTitle")
        title = title_element.text if title_element else "Title not found"
        description_element = driver.find_element(By.ID, "productDescription_feature_div")
        description = description_element.text if description_element else "Description not found"
        image_element = driver.find_element(By.ID, "landingImage")
        image_url = image_element.get_attribute("src") if image_element else "Image URL not found"


        return title, image_url, description
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None, None, None
    finally:
        driver.quit()


title, image_url, description = get_book_details(book_link)

print("Book Title:", title)
print("Book Image URL:", image_url)
print("Book Description:", description)

# def market_book(post_data, user_email=user_email):
#     title = post_data["title"]
#     body = post_data["body"]
#     original_url = post_data["url"]  # URL from the RSS feed
#
#     # Append the original post URL to the body
#     body_with_url = f"{body}\n\nOriginal post: {original_url}"
#
#     description = body_with_url  # Or however you want to set the description
#
#     # Ensure the data is URL-encoded to handle special characters
#     from urllib.parse import quote
#     title_encoded = quote(title)
#     body_encoded = quote(body_with_url)
#     description_encoded = quote(description)
#
#     # Construct the URL with the encoded data
#     url = (f"https://app.circle.so/api/v1/posts?"
#            f"community_id={community_id}&"
#            f"space_id={space_id}&"
#            f"name={title_encoded}&body={body_encoded}&"
#            f"is_pinned=false&is_comments_enabled=true&"
#            f"is_comments_closed=false&is_liking_enabled=true&"
#            f"skip_notifications=false&"
#            f"meta_title={title_encoded}&meta_description={description_encoded}&"
#            f"opengraph_title={title_encoded}&opengraph_description={description_encoded}&"
#            f"hide_from_featured_areas=false")
#     if user_email:
#         url += f"&user_email={quote(user_email)}"
#     headers = {
#         "Authorization": f"{circle_token}"
#     }
#
#     # Make a POST request to create the post in Circle
#     response = requests.post(url, headers=headers)
#     return response.json()
