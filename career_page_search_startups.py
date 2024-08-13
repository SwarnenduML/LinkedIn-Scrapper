import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import pandas as pd


def find_career_page(website):
    potential_keywords = ['careers', 'jobs', 'join-us', 'work-with-us', 'employment']
    try:
        response = requests.get(website, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for any anchor tags that might lead to a career page based on href or text
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].lower()
            text = a_tag.get_text(strip=True).lower()

            # Check if the href or the visible text contains any of the keywords
            if any(keyword in href for keyword in potential_keywords) or \
                    any(keyword in text for keyword in potential_keywords):
                return urljoin(website, a_tag['href'])  # Convert to absolute URL

        return "Career page not found"
    except Exception as e:
        return str(e)


def main():
    input_data = pd.read_csv("german_startups.csv")

    career_pages = []

    print("Searching for career pages...")
    for name, website in input_data:
        print(f"Processing {name} ({website})...")
        career_page = find_career_page(website)
        career_pages.append({"Name": name, "Website": website, "Career Page": career_page})

    output_file = 'company_career_pages.csv'
    keys = career_pages[0].keys()

    with open(output_file, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(career_pages)

    print(f"Career pages saved to 'company_career_pages.csv'.")


if __name__ == "__main__":
    main()
