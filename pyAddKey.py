import yaml

# Input- und Output-Dateien
input_file = "add"
output_file = "add.yaml"

# Lade die YAML-Datei ein
with open(input_file, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

# Verändere das Format der Antworten
for key, value in data['antworten'].items():
    # Value ist eine Liste, wir fügen den Key als String vor den Response
    data['antworten'][key] = [f" '{key}': {response}" for response in value]

# Speichere das neue YAML-Format in die Ausgabedatei
with open(output_file, 'w', encoding='utf-8') as file:
    yaml.dump(data, file, allow_unicode=True, default_flow_style=False)

print(f"Umwandlung abgeschlossen: {output_file}")

def yaml_to_js(file_path):
    # Lade die YAML-Datei
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    # Beginne die JS-Daten, die angehängt werden sollen
    js_output = ""

    # Iteriere durch den YAML-Inhalt und bereite den neuen Inhalt vor
    for key, value in data['antworten'].items():
        js_output += f'  "{key}": [\n'
        for response in value:
            js_output += f'    "{response}",\n'
        js_output += "  ],\n"

    # Entferne die letzte Zeile '};' aus der Datei
    with open('responses.js', 'r+', encoding='utf-8') as js_file:
        lines = js_file.readlines()
        
        # Entferne die letzte Zeile
        if lines[-1].strip() == "};":
            lines = lines[:-1]
        
        # Gehe zurück an den Anfang der Datei und schreibe die bearbeiteten Zeilen
        js_file.seek(0)
        js_file.writelines(lines)
        js_file.truncate()  # Entferne den restlichen Inhalt, falls vorhanden

    # Füge den neuen Inhalt hinzu und schließe die Konstante wieder mit '};'
    with open('responses.js', 'a', encoding='utf-8') as js_file:
        js_file.write(js_output)
        js_file.write("};\n")

    print("Neuer Inhalt wurde in 'responses.js' eingefügt.")

# Beispielnutzung
if __name__ == "__main__":
    yaml_file = 'add.yaml'  # Pfad zur YAML-Datei
    yaml_to_js(yaml_file)
