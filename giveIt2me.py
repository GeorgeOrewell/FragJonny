import re
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import wget

# Definiere benutzerdefinierte Header (Disguise Header)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Erstelle ein Verzeichnis, um die Ressourcen zu speichern
def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# Lade eine Ressource herunter
def download_resource(url, output_dir):
    resource_name = url.split("/")[-1]
    resource_path = os.path.join(output_dir, resource_name)

    if not os.path.exists(resource_path):
        create_directory(output_dir)
        try:
            wget.download(url, out=output_dir)
            print(f"\nRessource heruntergeladen: {resource_name}")
        except Exception as e:
            print(f"\nFehler beim Herunterladen der Ressource {url}: {e}")
    else:
        print(f"\nRessource bereits vorhanden: {resource_name}, überspringe Download.")

# Optisch ansprechende Anzeige der Ressourcenliste
def display_resources(resources):
    print("\n" + "=" * 50)
    print(f"Gefundene Ressourcen ({sum(len(urls) for urls in resources.values())} insgesamt):")
    print("=" * 50)
    
    for i, (resource_type, urls) in enumerate(resources.items(), 1):
        print(f"\n[{i}] {resource_type.capitalize()} ({len(urls)} gefunden):")
        for j, url in enumerate(urls, 1):
            print(f"  {j}. {url}")
    print("\n" + "=" * 50)

# Ressourcenauswahl durch Nummerneingabe
def select_resources(resources):
    selected_resources = []
    
    for resource_type, urls in resources.items():
        print(f"\nWelche {resource_type.capitalize()} möchten Sie herunterladen?")
        print("Geben Sie die Nummern ein, getrennt durch Komma oder Leerzeichen (z.B. 1,3,5 oder 1 3 5):")
        
        for j, url in enumerate(urls, 1):
            print(f"  {j}. {url}")
        
        selected_input = input("\nIhre Auswahl: ")
        selected_nums = re.split(r'[,\s]+', selected_input.strip())  # Trennung durch Komma oder Leerzeichen
        
        for num in selected_nums:
            if num.isdigit() and 1 <= int(num) <= len(urls):
                selected_resources.append(urls[int(num) - 1])
    
    return selected_resources

# Finde und klassifiziere Ressourcen nach Typ
def find_resources(page_content, base_url):
    soup = BeautifulSoup(page_content, "html.parser")
    resources = {
        "images": [],
        "videos": [],
        "scripts": [],
        "css": []
    }

    # Finde alle Bilder
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if img_url:
            img_url = urljoin(base_url, img_url)
            resources["images"].append(img_url)

    # Finde alle Videos
    for video in soup.find_all("video"):
        video_url = video.get("src")
        if video_url:
            video_url = urljoin(base_url, video_url)
            resources["videos"].append(video_url)

    # Finde alle CSS-Dateien
    for css in soup.find_all("link", rel="stylesheet"):
        css_url = css.get("href")
        if css_url:
            css_url = urljoin(base_url, css_url)
            resources["css"].append(css_url)

    # Finde alle JS-Dateien
    for script in soup.find_all("script"):
        script_url = script.get("src")
        if script_url:
            script_url = urljoin(base_url, script_url)
            resources["scripts"].append(script_url)

    return resources

# Lade die Seite herunter und finde Ressourcen
def download_page_and_resources(url, output_dir):
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(f"Seite erfolgreich geladen: {url}")
        
        resources = find_resources(response.text, url)
        display_resources(resources)
        
        # Benutzer wählt Ressourcen aus
        selected_resources = select_resources(resources)
        
        # Lade ausgewählte Ressourcen herunter
        if selected_resources:
            print("\nStarte den Download der ausgewählten Ressourcen...")
            for resource in selected_resources:
                download_resource(resource, output_dir)
        else:
            print("Keine Ressourcen zum Download ausgewählt.")
    else:
        print(f"Fehler beim Laden der Seite: {url}")

if __name__ == "__main__":
    url = input("Bitte die URL der Website eingeben: ")
    output_dir = input("Bitte das Verzeichnis angeben, in das die Dateien heruntergeladen werden sollen: ")
    
    create_directory(output_dir)
    download_page_and_resources(url, output_dir)
