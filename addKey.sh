#!/bin/bash

# Dateiname als Parameter übergeben
DATEI=$1
mv "$DATEI" "$DATEI.backup"
# Ausgabe-Datei, um die modifizierte Datei zu speichern
AUSGABE_DATEI="${DATEI}"
DATEI=$DATEI.backup


# Temporäre Variablen
key=""
answer=""

# Funktion, um Schlüssel und Antworten zu extrahieren und zu modifizieren
function modify_file() {
  # Neue Datei wird erstellt oder überschrieben
  > "$AUSGABE_DATEI"

  # Lese die Datei Zeile für Zeile
  while IFS= read -r line; do
    # Suche nach dem Schlüssel (z.B. "test")
    if [[ $line =~ \"([^\"]+)\": ]]; then
      key=${BASH_REMATCH[1]}
    fi

    # Suche nach der Antwort (z.B. "Ja, Test war erfolgreich. Du kannst aufatmen, ich funktioniere!")
    if [[ $line =~ \"([^\"]+)\" ]]; then
      answer=${BASH_REMATCH[1]}

      # Überprüfen, ob der Schlüssel bereits in der Antwort enthalten ist
      if [[ $answer != " '$key':"* ]]; then
        # Modifiziere die Antwort, indem der Schlüssel (Frage) hinzugefügt wird
        modified_answer=" '$key': $answer"
        # Ersetze die alte Antwort durch die neue, modifizierte Antwort in der Zeile
        line=${line/$answer/$modified_answer}
      fi
    fi

    # Schreibe die modifizierte Zeile in die neue Datei
    echo "$line" >> "$AUSGABE_DATEI"
  done < "$DATEI"

  echo "Datei wurde erfolgreich modifiziert: $AUSGABE_DATEI"
}

# Aufruf der Funktion und Übergabe der Datei
modify_file
