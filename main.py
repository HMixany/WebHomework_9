import requests
import json
from bs4 import BeautifulSoup

base_url = 'https://quotes.toscrape.com/'


def get_page_content(url):
    response = requests.get(url)
    content = BeautifulSoup(response.text, 'html.parser')
    return content


def parse_quotes(content):
    quotes = []
    authors_href = []
    quotes_divs = content.find_all('div', attrs={'class': 'quote'})
    for quote_div in quotes_divs:
        tags = []
        quote_span = quote_div.find('span', attrs={'class': 'text'}).string.strip()
        author_name = quote_div.find('small', attrs={'class': 'author'}).string.strip()
        tags_a = quote_div.find_all('a', attrs={'class': 'tag'})
        for tag in tags_a:
            tags.append(tag.string.strip())
        quotes.append({'quote': quote_span, 'author': author_name, 'tags': tags})
        authors_url = base_url + quote_div.find("a").get("href") + '/'
        authors_href.append(authors_url)
    return quotes, authors_href


def parse_authors(content):
    author_fullname = content.find('h3', attrs={'class': 'author-title'}).string.strip()
    born_date = content.find('span', attrs={'class': 'author-born-date'}).string.strip()
    born_location = content.find('span', attrs={'class': 'author-born-location'}).string.strip()
    description = content.find('div', attrs={'class': 'author-description'}).string.strip()
    result = {
        "fullname": author_fullname, "born_date": born_date, "born_location": born_location, "description": description
    }
    return result


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def main():
    result_by_quotes = []
    result_by_authors = []
    authors_urls = []
    page_content = get_page_content(base_url)
    quotes_data, authors = parse_quotes(page_content)
    authors_urls.extend(authors)
    result_by_quotes.extend(quotes_data)
    while True:
        next_page_link = page_content.find('li', class_='next')
        if not next_page_link:
            break
        next_page_url = base_url + next_page_link.find('a').get("href")
        page_content = get_page_content(next_page_url)
        quotes_data, authors = parse_quotes(page_content)
        authors_urls.extend(authors)
        result_by_quotes.extend(quotes_data)

    authors_urls = list(set(authors_urls))
    for author_url in authors_urls:
        page_content = get_page_content(author_url)
        result_by_authors.append(parse_authors(page_content))

    save_to_json(result_by_quotes, 'quotes.json')
    save_to_json(result_by_authors, 'authors.json')


if __name__ == '__main__':
    main()
