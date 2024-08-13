import csv
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd

linkedin_login_url = 'https://www.linkedin.com/login'
linkedin_username = 'swarnendusengupta29@gmail.com'  # Replace with your LinkedIn email
linkedin_password = 'Delight@2909@'  # Replace with your LinkedIn password
job_title = 'Machine Learning'
location = 'Germany'

def setup_driver():
    edge_options = Options()
    edge_options.add_argument("--start-maximized")
#    edge_options.add_argument("--headless")  # Run in headless mode (no browser window)
    driver = webdriver.Edge(options=edge_options)
    return driver


def go_to_page(page_number):
    try:
        # Find the pagination container
        pagination_container = driver.find_element(By.CLASS_NAME, 'artdeco-pagination__pages')

        # Find the desired page number button
        desired_page_button = pagination_container.find_element(By.XPATH, f'.//button[text()="Page {page_number}"]')

        # Click the desired page number
        desired_page_button.click()

        # Wait for the next page to load
        time.sleep(3)  # Adjust sleep time as necessary
        print(f"Moved to page {page_number}")

    except Exception as e:
        print(f"An error occurred: {e}")

def scroll_within_container(container):
    last_height = driver.execute_script("return arguments[0].scrollHeight", container)
    while True:
        # Scroll down within the container
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', container)
        for i in range(10):
            container.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == last_height:
            break
        last_height = new_height


def login_to_linkedin(driver, username, password, job_title, location):
    driver.get(linkedin_login_url)

    # Allow page to load
    time.sleep(2)

    # Find and fill the username and password input fields
    username_input = driver.find_element(By.ID, 'username')
    password_input = driver.find_element(By.ID, 'password')

    username_input.send_keys(username)
    password_input.send_keys(password)

    # Submit the form
    password_input.send_keys(Keys.RETURN)

    # Allow time for login to complete
    time.sleep(5)

    # Navigate to the LinkedIn job search page with the given job title and location
    driver.get(
        f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"
    )
    time.sleep(2)

    # Scroll through the first 50 pages of search results on LinkedIn
    for i in range(0,10):

        # Log the current page number
        print(f"Scrolling to bottom of page {i}...")

        # Locate the left side element by its class name or ID
        left_side_element = driver.find_element(By.CLASS_NAME, 'jobs-search-results__list-item')

        scroll_within_container(left_side_element)

        # Get the HTML of the <ul> element
        ul_html = left_side_element.get_attribute('innerHTML')

        # Scroll within the specific element
        scroll_pause_time = 2  # Pause time between scrolls

        # Wait for a random amount of time before scrolling to the next page
        time.sleep(random.choice(list(range(3, 7))))

        # Scrape the job postings
        jobs = []

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(ul_html, 'html.parser')

        # Find all <li> elements within the <ul> element
        li_elements = soup.find_all('li', class_='jobs-search-results__list-item')

        for li in li_elements:
            # Extract job details

            # Position title
            if li.find('a', class_='job-card-list__title'):# or li.find('a',class_=):
                position = li.find('a', class_='job-card-list__title').get_text(strip=True)

                # Job link (href)
                job_link = li.find('a', class_='job-card-list__title')['href']

                # Company name
                company_name = li.find('span', class_='job-card-container__primary-description').get_text(strip=True)

                # Location
                location = li.find('li', class_='job-card-container__metadata-item').get_text(strip=True)

                # Additional details like "Viewed", "Promoted", etc.
                job_state = li.find('li', class_='job-card-container__footer-item job-card-container__footer-job-state')
                job_state = job_state.get_text(strip=True) if job_state else "N/A"

                promoted = li.find('li', text='Promoted')
                promoted = "Yes" if promoted else "No"

                applicants = li.find('strong').get_text(strip=True)

                jobs.append(
                    {
                        "title": position,
                        "company": company_name,
                        "link": 'https://www.linkedin.com'+job_link,
                        "location": location,
                        "job state": job_state,
                        "promoted by linkedIn": promoted,
                        "seen on": datetime.today().strftime('%d-%m-%Y'),
                        "aaplicants": applicants,
                    }
                )
                # Logging scrapped job with company and location information
                print(f'Scraped "{position}" at {company_name}')
            else:
                print(li.text)

        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'text-heading-medium card-upsell-v2__headline')))


        # Example Usage:
        go_to_page(i+1)   # To go to a specific page number, e.g., page 3

    return jobs


if __name__ == "__main__":
    driver = setup_driver()
    jobs = login_to_linkedin(driver,linkedin_username,linkedin_password, job_title, location)
    output_file = 'company_career_pages.csv'
    keys = jobs[0].keys()

    with open(output_file, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(jobs)
