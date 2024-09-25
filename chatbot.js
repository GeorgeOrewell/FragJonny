// Dummy-YAML-Inhalte (ersetze dies durch den Inhalt der Datei oder einen Fetch-Request)
const yamlData = `
antworten:
  Alexander der Große:
    - "Ein mazedonischer König und Militärstratege, der das größte Reich der Antike aufbaute. Sein Eroberungsfeldzug reichte von Griechenland bis Indien und verbreitete die hellenistische Kultur."
  
  Kleopatra:
    - "Die letzte Pharaonin Ägyptens, die für ihre politischen Allianzen mit Julius Caesar und Mark Anton bekannt ist. Ihre Herrschaft markierte das Ende der ägyptischen Unabhängigkeit."

  Julius Caesar:
    - "Ein römischer General und Diktator, der bedeutende politische und soziale Reformen einführte. Sein Aufstieg zur Macht und seine Ermordung führten zum Ende der Römischen Republik und dem Beginn des Römischen Kaiserreichs."
  
  Marie Curie:
    - "Eine polnisch-französische Physikerin und Chemikerin, die für ihre Forschung über Radioaktivität bekannt ist. Sie war die erste Frau, die einen Nobelpreis erhielt, und die einzige Person, die Nobelpreise in zwei wissenschaftlichen Disziplinen gewann."
  
  Albert Einstein:
    - "Ein deutscher theoretischer Physiker, der die Relativitätstheorie entwickelte, die unser Verständnis von Raum, Zeit und Gravitation revolutionierte. Er gilt als einer der bedeutendsten Wissenschaftler des 20. Jahrhunderts."
`;

// YAML parsen
const responses = jsyaml.load(yamlData);

// Funktion zur Berechnung der Ähnlichkeit zwischen zwei Strings
function getSimilarityScore(str1, str2) {
  let matches = 0;
  const words1 = str1.toLowerCase().split(" ");
  const words2 = str2.toLowerCase().split(" ");
  
  words1.forEach(word1 => {
    if (words2.includes(word1)) {
      matches++;
    }
  });
  
  return matches / Math.max(words1.length, words2.length);
}

// Funktion zum Abgleich der Benutzereingabe
function getResponse(userInput) {
  const answers = responses.antworten;
  let bestMatch = null;
  let highestScore = 0;

  for (const key in answers) {
    const score = getSimilarityScore(userInput, key);
    if (score > highestScore) {
      highestScore = score;
      bestMatch = key;
    }
  }

  // Rückgabe der besten Antwort oder eine Standardantwort
  return bestMatch ? answers[bestMatch][0] : "Entschuldigung, das habe ich nicht verstanden.";
}

// Event-Listener für den Button
document.getElementById('send-button').addEventListener('click', function() {
  const userInput = document.getElementById('user-input').value;
  const chatOutput = document.getElementById('chat-output');

  if (userInput) {
    // Zeige die Benutzereingabe im Chat
    chatOutput.innerHTML += `<p><strong>Du:</strong> ${userInput}</p>`;
    document.getElementById('user-input').value = '';

    // Antwort basierend auf der YAML-Datei auswählen
    const botResponse = getResponse(userInput);
    chatOutput.innerHTML += `<p><strong>Bot:</strong> ${botResponse}</p>`;
  }
});
