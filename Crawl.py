import os
import requests
from bs4 import BeautifulSoup
import wget
from urllib.parse import urljoin, urlparse
import re

# Konstante für maximale Scraping-Tiefe
MAX_DEPTH = 2

# Schalter zum Ein-/Ausschalten des Downloads bestimmter Ressourcen
DOWNLOAD_IMAGES = True
DOWNLOAD_VIDEOS = True
DOWNLOAD_SCRIPTS = True
DOWNLOAD_CSS = True

# Definiere den benutzerdefinierten Header (Disguise Header)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Erstelle ein Verzeichnis, um die Website zu speichern
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)  # Rekursive Erstellung des Verzeichnisses

# Lade die Seite herunter
def download_page(url, output_dir):
    response = requests.get(url, headers=headers)  # Benutze den benutzerdefinierten Header
    if response.status_code == 200:
        page_name = "index.html" if urlparse(url).path == "" or urlparse(url).path == "/" else urlparse(url).path.strip("/")
        
        # Stelle sicher, dass immer eine .html-Erweiterung vorhanden ist
        if not page_name.endswith(".html"):
            page_name += ".html"

        full_path = os.path.join(output_dir, page_name)
        if not os.path.exists(full_path):  # Prüfe, ob die Datei bereits existiert
            create_directory(os.path.dirname(full_path))  # Erstelle das Verzeichnis, falls es nicht existiert
            adjusted_content = adjust_links(response.text, url, output_dir)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(adjusted_content)
            print(f"Seite heruntergeladen: {url}")
        else:
            print(f"Seite bereits vorhanden: {url}")
        return response.text
    else:
        print(f"Fehler beim Herunterladen der Seite: {url}")
        return None

# Funktion zum Anpassen der Links in der HTML-Datei
def adjust_links(page_content, base_url, output_dir):
    soup = BeautifulSoup(page_content, "html.parser")
    domain_keyword = urlparse(base_url).netloc.split('.')[-2]  # Verwende ein Keyword der Domain
    
    # Alle Links in <a>, <img>, <link> und <script> Tags anpassen
    for tag in soup.find_all(["a", "img", "link", "script"], href=True, src=True):
        href = tag.get("href") or tag.get("src")  # Je nach Tag "href" oder "src"
        
        # Wenn der Link eine vollständige URL ist und den Domainnamen enthält
        if domain_keyword in href:
            # Mach den Link relativ zur Website-Struktur
            href = href.replace(f"https://{domain_keyword}.", "").replace(f"http://{domain_keyword}.", "")
        elif href.startswith("/"):
            href = href.lstrip("/")  # Entferne das führende "/"
        
        # Anhängen von .html bei Links zu HTML-Seiten ohne Erweiterung
        if tag.name == "a" and not href.endswith(".html"):
            href += ".html"

        # Aktualisiere den href oder src
        if tag.name == "a" or tag.name == "link":
            tag['href'] = href
        elif tag.name == "img" or tag.name == "script":
            tag['src'] = href

    return str(soup)

# Ressourcen herunterladen
def download_resource(url, output_dir):
    print(f"Url: {url} Dir: {output_dir}")
    create_directory(output_dir)

    # Extrahiere den Dateinamen aus der URL
    resource_name = url.split("/")[-1]
    resource_path = os.path.join(output_dir, resource_name)

    # Überprüfe, ob die Ressource bereits existiert
    if os.path.exists(resource_path):
        print(f"Ressource bereits vorhanden: {resource_name}, überspringe Download.")
        return

    # Überprüfe, ob die URL ein gültiger Dateityp ist (nicht z.B. data:image/base64)
    if url.startswith("data:"):
        print(f"Ungültige Ressource (data-URL), überspringe: {url}")
        return

    # Lade die Ressource herunter
    try:
        resource = wget.download(url, out=output_dir)
        print(f"\nRessource heruntergeladen: {resource}")
    except Exception as e:
        print(f"\nFehler beim Herunterladen der Ressource {url}: {e}")

# Finde und lade alle Ressourcen auf der Seite
def find_and_download_resources(page_content, base_url, output_dir):
    soup = BeautifulSoup(page_content, "html.parser")

    # Finde und lade alle Bilder
    if DOWNLOAD_IMAGES:
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if img_url:
                img_url = urljoin(base_url, img_url)
                download_resource(img_url, output_dir)

    # Finde und lade alle Videos
    if DOWNLOAD_VIDEOS:
        for video in soup.find_all("video"):
            video_url = video.get("src")
            if video_url:
                video_url = urljoin(base_url, video_url)
                download_resource(video_url, output_dir)

    # Finde und lade alle CSS-Dateien
    if DOWNLOAD_CSS:
        for css in soup.find_all("link", rel="stylesheet"):
            css_url = css.get("href")
            if css_url:
                css_url = urljoin(base_url, css_url)
                download_resource(css_url, output_dir)

    # Finde und lade alle JS-Dateien
    if DOWNLOAD_SCRIPTS:
        for script in soup.find_all("script"):
            script_url = script.get("src")
            if script_url:
                script_url = urljoin(base_url, script_url)
                download_resource(script_url, output_dir)

# Finde alle Links auf der Seite
def find_links(page_content, base_url):
    soup = BeautifulSoup(page_content, "html.parser")
    links = set()

    domain_keyword = urlparse(base_url).netloc.split('.')[-2]  # Verwende ein Keyword der Domain

    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href")
        if href:
            full_url = urljoin(base_url, href)
            # Füge nur Links zur Liste hinzu, die den Domainnamen enthalten
            if domain_keyword in full_url:
                links.add(full_url)
    return links

# Rekursiv alle Seiten bis zu einer bestimmten Tiefe herunterladen
def download_website(url, depth=0, visited=None):
    if visited is None:
        visited = set()

    if depth > MAX_DEPTH or url in visited:
        return

    visited.add(url)

    # Verzeichnis basierend auf der URL-Struktur erstellen
    parsed_url = urlparse(url)
    domain_name = parsed_url.netloc
    path = parsed_url.path.strip("/")
    output_dir = os.path.join(domain_name, path)

    # Lade die Hauptseite herunter
    page_content = download_page(url, output_dir)
    if page_content:
        find_and_download_resources(page_content, url, output_dir)

        # Finde und lade verlinkte Unterseiten
        links = find_links(page_content, url)
        for link in links:
            download_website(link, depth + 1, visited)

if __name__ == "__main__":
    url = input("Bitte die URL der Website eingeben: ")
    MAX_DEPTH = int(input("Maximale Scraping-Tiefe eingeben: "))
    print("Ressourcen auswählen (j = Ja, n = Nein):")
    DOWNLOAD_IMAGES = input("Bilder herunterladen? (j/n): ").lower() == "j"
    DOWNLOAD_VIDEOS = input("Videos herunterladen? (j/n): ").lower() == "j"
#    DOWNLOAD_SCRIPTS = input("JavaScript-Dateien herunterladen? (j/n): ").lower() == "j"
#    DOWNLOAD_CSS = input("CSS-Dateien herunterladen? (j/n): ").lower() == "j"

    download_website(url)
