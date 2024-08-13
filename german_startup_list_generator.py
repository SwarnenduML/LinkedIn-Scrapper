import requests
from bs4 import BeautifulSoup
import csv


def scrape_startups(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    startups = []

    # Find all startup entries
    entries = soup.find_all('article', id='failed-startup-text')[1]

    if entries:
        startup_names = entries.find_all('h3')
        website_links = entries.find_all('a', string="here")

        for name, link in zip(startup_names, website_links):
            startup_name = name.get_text(strip=True)
            website = link['href']
            startups.append({'Name': startup_name, 'Website': website})
    return startups


def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def main():
    url = "https://www.failory.com/startups/germany"  # The URL of the page
    print("Scraping startups from the given URL...")

    startups = scrape_startups(url)

    if startups:
        save_to_csv(startups, 'german_startups.csv')
        print(f"Data successfully written to 'german_startups.csv'.")
    else:
        print("No startups found.")


if __name__ == "__main__":
    main()
