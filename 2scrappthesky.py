import requests
from bs4 import BeautifulSoup
import sys
import time
import urllib.parse
import json
from rapidfuzz import fuzz
import signal
import os

# Konstanten für das Skript
SLEEP_TIME = 1  # Sekunden zwischen den Anfragen
MAX_URLS = 6  # Maximale Anzahl von URLs pro Suchbegriff
SIMILARITY_THRESHOLD = 75  # Mindest-Ähnlichkeit für fuzzy matching (0-100)
TIMEOUT_DURATION = 20  # Zeit in Sekunden, nach der der Scraping-Prozess abgebrochen wird
MAX_WORDS = 80  # Maximale Anzahl der Wörter für eine Content-Warnung
MAX_CHARACTERS = 600  # Maximale Anzahl der Zeichen für eine Content-Warnung

# Log-Datei für Suchbegriffe und Warnungen
log_file = "scraping_log.txt"

# Suchmaschinen URLs
search_engines = {
    "bing": "https://www.bing.com/search?q=",
    "yahoo": "https://search.yahoo.com/search?p="
}

# Bevorzugte Domains für Ergebnisse
preferred_domains = ["wikipedia.de", "wikipedia.org"]

# Ausgabe-Datei für JSON-Daten
output_json = "antworten.json"

# Timeout-Handler zur Handhabung von Zeitüberschreitungen
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

# Signal-Handler für Timeout
signal.signal(signal.SIGALRM, timeout_handler)

def search(query):
    """Durchsuche die Suchmaschinen nach dem Suchbegriff, beginnend mit Bing und dann Yahoo."""
    search_engines_list = ["bing", "yahoo"]  # Liste der Suchmaschinen in Reihenfolge

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    for search_engine in search_engines_list:
        search_url = search_engines[search_engine] + urllib.parse.quote(query + " wikipedia")
        try:
            print(f"Suche mit {search_engine} nach: {query}")
            signal.alarm(TIMEOUT_DURATION)  # Setze Timeout für jede Suchmaschine
            response = requests.get(search_url, headers=headers)
            signal.alarm(0)
            
            if response.status_code == 200:
                return response.text, search_engine  # Rückgabe von HTML und Suchmaschinenname
            else:
                print(f"Fehler bei der Suche mit {search_engine}: Status-Code {response.status_code}")
        except TimeoutException:
            print(f"Timeout bei der Suche mit {search_engine}. Fahre mit der nächsten Suchmaschine fort.")
        except Exception as e:
            print(f"Fehler bei der Suche mit {search_engine}: {e}")
    return None, None  # Wenn keine Suchmaschine erfolgreich war

def shorten_text(text):
    """Kürze den Text nach dem ersten vollständigen Satz."""
    parts = text.split('\n')
    end_characters = [".", "!", "?"]
    new_string = ""
    
    for part in parts:
        new_string += part
        if new_string and new_string[-1] in end_characters:
            break
    return new_string

def shorten_text_again(text):
    """Kürze den Text auf die ersten 6 Sätze."""
    sentences = text.split(".")
    return ".".join(sentences[:6]) + "." if len(sentences) >= 3 else text

def extract_links(html, search_engine):
    """Extrahiere Links aus den Suchergebnissen der angegebenen Suchmaschine."""
    soup = BeautifulSoup(html, 'html.parser')
    
    if search_engine == "bing":
        results = soup.find_all('a')
    elif search_engine == "yahoo":
        results = soup.find_all('a')

    links = []
    for result in results:
        link = result.get('href')
        if link and link.startswith("http"):
            links.append(link)

    # Links nach den bevorzugten Domains sortieren
    links.sort(key=lambda url: any(domain in url for domain in preferred_domains), reverse=True)
    return links

def scrape_content(url):
    """Scrape den Inhalt von der angegebenen URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        
        # Zusammensetzen des Inhalts aus den Paragraphen
        content = " ".join([p.get_text() for p in paragraphs])
        text = shorten_text(content)
        text = shorten_text_again(text)
        return text
    except Exception as e:
        print(f"Fehler beim Scrapen von {url}: {e}")
        return ""

def fuzzy_match(query, content):
    """Überprüfe, ob der Inhalt einen ähnlichen Satz zum Suchbegriff enthält."""
    sentences = content.split(".")
    for sentence in sentences:
        ratio = fuzz.partial_ratio(query.lower(), sentence.lower())
        if ratio >= SIMILARITY_THRESHOLD:
            return True
    return False

def log_warning(message):
    """Protokolliere Warnungen in der Log-Datei."""
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + "\n")

def load_existing_results():
    """Lade bestehende Ergebnisse aus der Log-Datei, wobei jeder Begriff in einer neuen Zeile steht."""
    existing_results = {}

    if os.path.exists('searchterms.log'):
        try:
            with open('searchterms.log', 'r', encoding='utf-8') as f:
                for line in f:
                    query = line.strip()
                    if query:  # Überspringt leere Zeilen
                        existing_results[query] = []  # Jeder Begriff hat eine leere Liste für die Ergebnisse
        except Exception as e:
            print(f"Fehler beim Laden der Datei 'searchterms.log': {e}")
            print("Die Datei scheint beschädigt zu sein. Es werden keine bestehenden Ergebnisse geladen.")
    return existing_results

def save_results(all_results):
    """Speichere die gesammelten Ergebnisse in einer JSON-Datei."""
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

def save_search_terms(terms):
    """Speichere die Suchbegriffe in der Log-Datei."""
    with open('searchterms.log', 'a', encoding='utf-8') as f:
        for term in terms:
            f.write(term + "\n")

def process_search_term(query, existing_results):
    """Verarbeite einen Suchbegriff und scrappe die relevanten Inhalte."""
    if query in existing_results:
        print(f"Suchbegriff '{query}' wurde bereits verarbeitet. Überspringe...")
        return None  # Suchbegriff wurde bereits verarbeitet

    results = {
        query: []
    }

    html, search_engine = search(query)  # Suche nach dem Begriff und erhalte die Suchmaschine
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
                    if not (content.endswith(":") or content.endswith(",") or content.endswith(";") or content.endswith("(")):
                        formatted_response = f"'{query}': {content}"
                        results[query].append(formatted_response)

                        # Warnungen für langen Inhalt
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
    """Hauptfunktion des Skripts."""
    existing_results = load_existing_results()  # Bestehende Ergebnisse laden
    all_results = {}

    # Suche nach .txt-Dateien im aktuellen Verzeichnis
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

    if not txt_files:
        print("Es sind keine .txt-Dateien im aktuellen Verzeichnis vorhanden.")
        sys.exit(1)

    # Nutzer nach der Datei fragen
    print("Bitte wähle eine Datei mit Suchbegriffen aus:")
    for i, file in enumerate(txt_files, start=1):
        print(f"{i}. {file}")

    while True:
        try:
            # Dateien zur Auswahl stellen
            choice = int(input("Gib die Nummer der Datei ein: ")) - 1
            if 0 <= choice < len(txt_files):
                search_terms_file = txt_files[choice]
                break
            else:
                print("Ungültige Auswahl. Bitte versuche es erneut.")
        except ValueError:
            print("Bitte gib eine gültige Zahl ein.")

    # Suchbegriffe aus der Datei laden
    with open(search_terms_file, 'r', encoding='utf-8') as f:
        search_terms = [line.strip() for line in f if line.strip()]

    if not search_terms:
        print("Die Datei enthält keine Suchbegriffe.")
        sys.exit(1)

    processed_queries = []
    for query in search_terms:
        if query in existing_results:
            print(f"Suchbegriff '{query}' wurde bereits verarbeitet.")
            continue

        result = process_search_term(query, existing_results)
        if result:
            all_results.update(result)
            processed_queries.append(query)  # Nur erfolgreich verarbeitete Suchbegriffe speichern

    # Ergebnisse in die JSON-Datei schreiben
    if all_results:
        save_results(all_results)

    # Neue Suchbegriffe in die Log-Datei schreiben
    if processed_queries:
        save_search_terms(processed_queries)

    print("Scraping abgeschlossen.")