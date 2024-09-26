// responses.js importiert die Antworten aus einer externen Datei
const stringList = ["ein", "für", "Hi", "Danke", "Ich", "was kennst du", "Okay",  "erzähl mir", "was ist", "wie funktioniert", "wer war", "wie geht", "was bedeutet", "in", "der", "die", " das ", " von ", " etwas ", "über", "welche", "kannst", "du", "reden", "mehr", "Gut", "was", "kennst", "für", "Warum", "Bitte", "Ja", "Nein", "Verstehe", "Hm", "Aha", "Also", "Echt?", "Cool", "Tschüss", "Bis bald", "Guten Morgen", "Gute Nacht", "Alles klar", "Schon gut", "Wie genau", "Wie funktioniert", "Kannst du", "Machst du", "weißt du", "Vielleicht", "Sozusagen", "Irgendwie", "Eben", "Tja", "Na ja", "Hmm"];


// Fuse.js Initialisierung mit den Daten
const fuseData = Object.keys(responses).map(key => ({
  name: key,
  response: responses[key][0]
}));

const fuse = new Fuse(fuseData, {
  keys: ['name'],        // Schlüssel, um nach den Namen zu suchen
  threshold: 0.4         // Threshold für Fuzzy-Suche, je niedriger, desto präziser
});

// Funktion, die den Bot dazu bringt, eine Antwort basierend auf der Nutzereingabe zu finden
function getBotReply(message) {
//  let cleanput = cleanString(message, stringList);
  const result = fuse.search(message); // Fuse.js verwendet die Suche

  if (result.length > 0) {
    // Rückgabe der Antwort basierend auf der besten Übereinstimmung
    return result[0].item.response;
  } else {
    // Wenn keine passende Antwort gefunden wird
    return "Tut mir leid, dazu wurden mir noch keine Daten hinterlegt. Vielleicht versuchst du mal nur den Begriff einzugeben.";
  }
}
// Funktion um den LogFile zu erstellen
function saveToLocalStorage(userMessage, botReply) {
  let chatLog = JSON.parse(localStorage.getItem('chatLog')) || [];
  chatLog.push({ user: userMessage, bot: botReply });
  localStorage.setItem('chatLog', JSON.stringify(chatLog));
}

// Selbsterklärend
function displayChatLog() {
  const outputDiv = document.getElementById("output");
  const chatLog = JSON.parse(localStorage.getItem('chatLog')) || [];
  chatLog.forEach(entry => {
    outputDiv.innerHTML += `<p><strong>Du:</strong> ${entry.user}</p>`;
    outputDiv.innerHTML += `<p><strong>Jonny:</strong> ${entry.bot}</p>`;
  });
}

// Rufe die Funktion beim Laden der Seite auf, um den bisherigen Chatverlauf anzuzeigen
window.onload = function() {
  displayChatLog();
};


function cleanString(inputString, stringList) {
  // Gehe durch jede Zeichenkette in der Liste
  stringList.forEach(substring => {
    // Ersetze alle Vorkommen des Substrings durch einen leeren String
    const regex = new RegExp(substring, 'g'); // 'g' steht für globales Ersetzen
    inputString = inputString.replace(regex, '');
  });

  // Gib den bereinigten String zurück
  return inputString;
}

// Funktion, die die Nachricht sendet und die Antwort im Chat anzeigt
function sendMessage() {
  const inputField = document.getElementById("userInput");
  const userMessage = inputField.value;
  const outputDiv = document.getElementById("output");

  if (userMessage.trim() !== "") {
    outputDiv.innerHTML += `<p><strong>Du:</strong> ${userMessage}</p>`;
    const botReply = getBotReply(userMessage);  // Hier wird die Fuzzy-Suche verwendet
    outputDiv.innerHTML += `<p><strong>Jonny:</strong> ${botReply}</p>`;
// Speichere im localStorage
    saveToLocalStorage(userMessage, botReply);

    inputField.value = "";
  }
}
