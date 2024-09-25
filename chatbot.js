function sendMessage() {
  const inputField = document.getElementById("userInput");
  const userMessage = inputField.value;
  const outputDiv = document.getElementById("output");

  if (userMessage.trim() !== "") {
    outputDiv.innerHTML += `<p><strong>Du:</strong> ${userMessage}</p>`;
    const botReply = getBotReply(userMessage);
    outputDiv.innerHTML += `<p><strong>Bot:</strong> ${botReply}</p>`;
    inputField.value = "";
  }
}

let responses = {}; // Globale Variable für die Antworten

function setConstResponses() {
  fetch('responses.yaml')
    .then(response => {
      if (!response.ok) {
        throw new Error('Netzwerkantwort war nicht ok');
      }
      return response.text(); // Die YAML-Datei als Text lesen
    })
    .then(data => {
      responses = parseYAML(data); // Die YAML-Daten in ein Objekt umwandeln
      console.log('Responses geladen:', responses);
    })
    .catch(error => {
      console.error('Es gab ein Problem mit dem Fetch-Vorgang:', error);
    });
}

// Funktion zum Parsen der YAML-Daten
function parseYAML(data) {
  const yamlLines = data.split('\n');
  const result = {};
  let currentKey = '';

  for (const line of yamlLines) {
    const trimmedLine = line.trim();
    if (trimmedLine === '') continue; // Leere Zeilen überspringen

    if (trimmedLine.endsWith(':')) {
      currentKey = trimmedLine.slice(0, -1); // Den Schlüssel ohne den Doppelpunkt speichern
      result[currentKey] = []; // Initialisiere ein Array für die Antworten
    } else {
      result[currentKey].push(trimmedLine.replace(/^- /, '').trim()); // Antworten zum Schlüssel hinzufügen
    }
  }
  return result;
}

// Diese Funktion wird aufgerufen, um eine Antwort zu erhalten
function getBotReply(message) {
  const responseList = responses[message] || ["Tut mir leid, ich verstehe dich nicht."];
  return responseList[Math.floor(Math.random() * responseList.length)];
}

// Rufe setConstResponses auf, um die Antworten beim Laden der Seite zu laden
setConstResponses();
