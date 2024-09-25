// Fuzzy-Logik: Levenshtein-Distanz zur Berechnung der Ähnlichkeit
function getLevenshteinDistance(a, b) {
    const matrix = [];

    // Initialisiere die erste Zeile
    for (let i = 0; i <= b.length; i++) {
        matrix[i] = [i];
    }

    // Initialisiere die erste Spalte
    for (let j = 0; j <= a.length; j++) {
        matrix[0][j] = j;
    }

    // Fülle die Matrix
    for (let i = 1; i <= b.length; i++) {
        for (let j = 1; j <= a.length; j++) {
            if (b.charAt(i - 1) === a.charAt(j - 1)) {
                matrix[i][j] = matrix[i - 1][j - 1]; // Keine Kosten
            } else {
                matrix[i][j] = Math.min(
                    matrix[i - 1][j - 1] + 1, // Ersetzen
                    Math.min(matrix[i][j - 1] + 1, // Einfügen
                              matrix[i - 1][j] + 1) // Löschen
                );
            }
        }
    }

    return matrix[b.length][a.length];
}

function getSimilarityScore(userInput, key) {
    const distance = getLevenshteinDistance(userInput.toLowerCase(), key.toLowerCase());
    const maxLen = Math.max(userInput.length, key.length);
    return (1 - distance / maxLen); // Ähnlichkeitswert zwischen 0 und 1
}

// Fetch-Request, um Antworten dynamisch zu laden
async function fetchAnswers() {
    try {
        const response = await fetch('https://raw.githubusercontent.com/GeorgeOrewell/FragJonny/main/responses.yaml'); // Ersetze durch die tatsächliche URL
        if (!response.ok) {
            throw new Error('Netzwerkantwort war nicht ok');
        }
        const data = await response.json();
        return data.antworten; // Annahme: Antworten sind im JSON-Feld "antworten"
    } catch (error) {
        console.error('Fehler beim Abrufen der Antworten:', error);
        return {}; // Rückgabe eines leeren Objekts im Fehlerfall
    }
}

// Funktion zur Auswahl der besten Antwort basierend auf Benutzer-Eingabe
async function getBestResponse(userInput) {
    const antworten = await fetchAnswers();
    let bestScore = 0;
    let bestResponse = '';

    for (const key in antworten) {
        const score = getSimilarityScore(userInput, key);
        if (score > bestScore) {
            bestScore = score;
            bestResponse = antworten[key][0]; // Nimm die erste Antwort
        }
    }

    return bestResponse || 'Keine passende Antwort gefunden.';
}

// Beispiel für die Verwendung
const userInput = "Albert Einstein"; // Beispielhafte Benutzereingabe
getBestResponse(userInput).then(response => {
    console.log(response);
});
