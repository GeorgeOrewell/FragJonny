import requests
from bs4 import BeautifulSoup
import sys
import time
import urllib.parse
import json
from rapidfuzz import fuzz
import signal
import os

# Konstanten
SLEEP_TIME = 1  # Sekunden zwischen den Anfragen
MAX_URLS = 5  # Maximale Anzahl von URLs pro Suchbegriff
SIMILARITY_THRESHOLD = 60  # Mindest-Ähnlichkeit für fuzzy matching (0-100)
TIMEOUT_DURATION = 10  # Zeit in Sekunden, nach der der Scraping-Prozess abgebrochen wird
MAX_WORDS = 1000  # Maximale Anzahl der Wörter für eine Content-Warnung
MAX_CHARACTERS = 5000  # Maximale Anzahl der Zeichen für eine Content-Warnung

# Log-Datei für Suchbegriffe und Warnungen
log_file = "scraping_log.txt"

# Suchmaschinen URLs
search_engines = {
    "bing": "https://www.bing.com/search?q=",
}

# Bevorzugte Domains
preferred_domains = ["wikipedia.org", "wikipedia.de"]

# Ausgabe-Datei für JSON-Daten
output_json = "antworten.json"

# Timeout-Handler
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

def search(search_engine, query):
    search_url = search_engines[search_engine] + urllib.parse.quote(query + " wikipedia")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Fehler bei der Suche mit {search_engine}: Status-Code {response.status_code}")
        return None

def shorten_text(text):
    parts = text.split("\n")
    end_characters = [".", "!", "?"]
    new_string = ""
    for part in parts:
        new_string += part
        if new_string and new_string[-1] in end_characters:
            break
    return new_string

def extract_links(html, search_engine):
    soup = BeautifulSoup(html, 'html.parser')
    if search_engine == "bing":
        results = soup.find_all('a')
    links = []
    for result in results:
        link = result.get('href')
        if link and link.startswith("http"):
            links.append(link)
    links.sort(key=lambda url: any(domain in url for domain in preferred_domains), reverse=True)
    return links

def scrape_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs])
        text = shorten_text(content)
        return text
    except Exception as e:
        print(f"Fehler beim Scrapen von {url}: {e}")
        return ""

def fuzzy_match(query, content):
    sentences = content.split(".")
    for sentence in sentences:
        ratio = fuzz.partial_ratio(query.lower(), sentence.lower())
        if ratio >= SIMILARITY_THRESHOLD:
            return True
    return False

def log_warning(message):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + "\n")

def load_existing_results():
    if os.path.exists(output_json):
        with open(output_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_results(all_results):
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

def process_search_term(query, existing_results):
    if query in existing_results:
        print(f"Suchbegriff '{query}' wurde bereits verarbeitet. Überspringe...")
        return None  # Suchbegriff wurde bereits verarbeitet

    results = {
        query: []
    }

    for search_engine in search_engines:
        html = search(search_engine, query)
        if html:
            links = extract_links(html, search_engine)
            url_count = 0  # Zähler für durchsuchte URLs

            for link in links:
                if url_count >= MAX_URLS:
                    break  # Breche ab, wenn die maximale Anzahl an URLs erreicht ist

                signal.alarm(TIMEOUT_DURATION)
                try:
                    content = scrape_content(link)
                    signal.alarm(0)

                    if fuzzy_match(query, content):
                        # Formatieren der Antwort
                        formatted_response = f"'{query}': {content}"
                        results[query].append(formatted_response)

                        if len(content.split()) > MAX_WORDS or len(content) > MAX_CHARACTERS:
                            log_warning(f"Warnung: Content für '{query}' ist sehr lang.")
                        return results  # Sobald ein Treffer gefunden wurde, verlasse die Schleife

                except TimeoutException:
                    print(f"Timeout beim Scrapen von {link}. Fahre mit der nächsten URL fort.")
                    continue
                except Exception as e:
                    print(f"Fehler beim Scrapen von {link}: {e}")
                    continue

                url_count += 1
                time.sleep(SLEEP_TIME)

    log_warning(f"Kein Treffer für Suchbegriff: '{query}'")
    return None

def main():
    existing_results = load_existing_results()  # Bestehende Ergebnisse laden
    all_results = existing_results.copy()

    # Suche nach .txt-Dateien im aktuellen Verzeichnis
    txt_files = [f for f in files.listdir('.') if f.endswith('.txt')]
    
    if not txt_files:
        print("Es sind keine .txt-Dateien im aktuellen Verzeichnis vorhanden.")
        sys.exit(1)

    # Nutzer nach der Datei fragen
    print("Bitte wähle eine Datei mit Suchbegriffen aus:")
    for i, file in enumerate(txt_files, start=1):
        print(f"{i}. {file}")
    while True:
        try:
            choice = int(input("Gib die Nummer der Datei ein: ")) - 1
            if 0 <= choice < len(txt_files):
                search_terms_file = txt_files[choice]
                break
            else:
                print("Ungültige Auswahl. Bitte versuche es erneut.")
        except ValueError:
            print("Bitte gib eine gültige Nummer ein.")

    try:
        with open(search_terms_file, 'r') as f:
            search_terms = f.read().splitlines()
    except FileNotFoundError:
        print(f"Datei {search_terms_file} wurde nicht gefunden.")
        sys.exit(1)

    for query in search_terms:
        print(f"Suche nach: {query}")
        result = process_search_term(query, existing_results)
        if result:
            all_results.update(result)  # Ergebnisse im gewünschten Format hinzufügen

    save_results(all_results)

    print(f"Suchvorgang abgeschlossen. Ergebnisse gespeichert in {output_json}")
    # Funktion zum abfragen des Anhängens an responses.js (Hauptdatei)
    append_to_responses_js('antworten.json', 'responses.js')

    # Log-Datei anzeigen und löschen, falls der Nutzer nicht anders entscheidet
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            if log_content:
                print("\nLog-Datei-Inhalt:")
                print(log_content)
        user_input = input("Möchtest du die Log-Datei behalten? (j/n): ").strip().lower()
        if user_input == "n":
            os.remove(log_file)
            print("Log-Datei wurde gelöscht.")
        else:
            print("Log-Datei wurde beibehalten.")


def append_to_responses_js(json_file, js_file):
    # Überprüfen, ob die Dateien existieren
    if not os.path.exists(json_file):
        print(f"Die Datei '{json_file}' existiert nicht.")
        return
    if not os.path.exists(js_file):
        print(f"Die Datei '{js_file}' existiert nicht.")
        return
    # Den Benutzer fragen, ob die Daten hinzugefügt werden sollen
    user_input = input("Möchtest du die Daten aus der JSON-Datei zur responses.js hinzufügen? (ja/nein): ").strip().lower()
    if user_input != "ja":
        print("Daten wurden nicht hinzugefügt.")
        return
    # JSON-Daten laden
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    # Die vorhandene responses.js-Datei laden und die letzten Zeilen abrufen
    with open(js_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Die Struktur der js-Datei beibehalten und die neuen Daten hinzufügen
    with open(js_file, 'w', encoding='utf-8') as f:
        for line in lines[:-1]:  # Alle Zeilen außer der letzten schreiben
            f.write(line)
        # Neuen Inhalt hinzufügen
        for key, value in json_data.items():
            f.write(f'    "{key}": {json.dumps(value)},\n')  # Füge die Daten im richtigen Format hinzu
        f.write(lines[-1])  # Die letzte Zeile (schließende geschweifte Klammer) schreiben
    print("Daten erfolgreich hinzugefügt.")

if __name__ == "__main__":
    main()
