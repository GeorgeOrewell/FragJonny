import yaml

def yaml_to_js(file_path):
    # Lade die YAML-Datei
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    # Beginne die JS-Datei
    js_output = "const responses = {\n"

    # Iteriere durch den YAML-Inhalt
    for key, value in data['antworten'].items():
        js_output += f'  "{key}": [\n'
        for response in value:
            js_output += f'    "{response}",\n'
        js_output += "  ],\n"

    js_output += "};"

    # Speichere das Ergebnis in eine JS-Datei
    with open('responses.js', 'w', encoding='utf-8') as js_file:
        js_file.write(js_output)

    print("Konvertierung abgeschlossen. Ergebnis in 'responses.js' gespeichert.")

# Beispielnutzung
if __name__ == "__main__":
    yaml_file = 'responses.yaml'  # Pfad zur YAML-Datei
    yaml_to_js(yaml_file)
