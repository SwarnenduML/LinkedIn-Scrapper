import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def google_search(company):
    # Create the URL for the Google search
    query = company + " career"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    # Make the request to the Google search page
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all the links in the search results
    links = []
    for item in soup.find_all('a'):
        href = item.get('href')
        if href and ("career" in href or "karrier" in href or "jobs" in href or "job" in href) and \
                company.lower() in href and "https" in href and "google" not in href:
            links.append(href)

    return links


# Example search query
def main():
    input_data = pd.read_csv("german_startups.csv")
    input_data['Company Name'] = input_data['Name'].str.split(')').str[1].str.strip()
    all_links = []
    for query in input_data['Company Name']:
        print(query)
        results = google_search(query)
        for result in results:
            all_links.append({'Company Name': query, 'Websites': result})

    save_to_csv(all_links, 'career_websites.csv')


if __name__ == "__main__":
    main()