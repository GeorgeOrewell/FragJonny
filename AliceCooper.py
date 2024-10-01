import requests
from bs4 import BeautifulSoup
import json
import os
import time

# Erlaubte Sprachen
ALLOWED_LANGUAGES = ['de', 'en']

# Dateien
visited_urls_file = "visited_urls.json"
metadata_file = "metadata.json"
url_queue_file = "url_queue.txt"

# Gefälschter User-Agent Header
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Lade bereits besuchte URLs
def load_visited_urls():
    if os.path.exists(visited_urls_file):
        with open(visited_urls_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Speichere besuchte URLs
def save_visited_urls(visited_urls):
    with open(visited_urls_file, 'w', encoding='utf-8') as f:
        json.dump(visited_urls, f, ensure_ascii=False, indent=4)

# Lade Warteschlange
def load_url_queue():
    if os.path.exists(url_queue_file):
        with open(url_queue_file, 'r', encoding='utf-8') as f:
            return f.read().splitlines()
    return []

# Füge URL zur Warteschlange hinzu
def add_to_url_queue(url):
    with open(url_queue_file, 'a', encoding='utf-8') as f:
        f.write(url + '\n')

# Lade Metadaten
def load_metadata():
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Speichere Metadaten
def save_metadata(metadata):
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

# Überprüfe die Sprache
def is_language_allowed(language):
    return language in ALLOWED_LANGUAGES

# Scrape eine URL
def scrape_url(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Metadaten extrahieren
        title = soup.title.string if soup.title else "Kein Titel"
        language = response.headers.get('Content-Language', 'en').split('-')[0]  # Nur den ersten Teil verwenden
        if is_language_allowed(language):
            metadata = {
                "url": url,
                "title": title,
                "language": language,
                "tags": [],
            }
            return metadata, extract_links(soup)
        else:
            print(f"Sprache '{language}' nicht erlaubt für URL: {url}")
            return None, []

    except Exception as e:
        print(f"Fehler beim Scrapen von {url}: {e}")
        return None, []

# Links extrahieren
def extract_links(soup):
    links = []
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']
        # Filtere Links, um nur absolute URLs zu behalten
        if link.startswith('http'):
            links.append(link)
    return links

# Hauptfunktion
def main():
    visited_urls = load_visited_urls()
    metadata_collection = load_metadata()
    url_queue = load_url_queue()

    while url_queue:
        url = url_queue.pop(0)
        if url in visited_urls:
            print(f"Bereits besuchte URL überspringen: {url}")
            continue
        
        metadata, found_links = scrape_url(url)
        if metadata:
            metadata_collection[url] = metadata
            visited_urls.append(url)
            print(f"Besuchte URL: {url}, Titel: {metadata['title']}")

            # Füge alle gefundenen Links zur Warteschlange hinzu, falls sie noch nicht besucht wurden
            for link in found_links:
                if link not in visited_urls:
                    add_to_url_queue(link)

        # Speichere die aktualisierten Daten regelmäßig
        save_visited_urls(visited_urls)
        save_metadata(metadata_collection)

        # Wartezeit zwischen den Anfragen
        time.sleep(1)

    print("Crawling abgeschlossen.")

if __name__ == "__main__":
    main()
