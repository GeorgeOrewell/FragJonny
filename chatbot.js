// responses.js importiert die Antworten aus einer externen Datei

// Fuse.js Initialisierung mit den Daten
const fuseData = Object.keys(responses).map(key => ({
  name: key,
  response: responses[key][0]
}));

const fuse = new Fuse(fuseData, {
  keys: ['name'],        // Schlüssel, um nach den Namen zu suchen
  threshold: 0.3         // Threshold für Fuzzy-Suche, je niedriger, desto präziser
});

// Funktion, die den Bot dazu bringt, eine Antwort basierend auf der Nutzereingabe zu finden
function getBotReply(message) {
  const result = fuse.search(message); // Fuse.js verwendet die Suche

  if (result.length > 0) {
    // Rückgabe der Antwort basierend auf der besten Übereinstimmung
    return result[0].item.response;
  } else {
    // Wenn keine passende Antwort gefunden wird
    return "Tut mir leid, ich verstehe dich nicht.";
  }
}

// Funktion, die die Nachricht sendet und die Antwort im Chat anzeigt
function sendMessage() {
  const inputField = document.getElementById("userInput");
  const userMessage = inputField.value;
  const outputDiv = document.getElementById("output");

  if (userMessage.trim() !== "") {
    outputDiv.innerHTML += `<p><strong>Du:</strong> ${userMessage}</p>`;
    const botReply = getBotReply(userMessage);  // Hier wird die Fuzzy-Suche verwendet
    outputDiv.innerHTML += `<p><strong>Bot:</strong> ${botReply}</p>`;
    inputField.value = "";
  }
}
