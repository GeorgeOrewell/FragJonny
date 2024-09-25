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

function getBotReply(message) {
  const responses = {
    "Hallo": "Hallo! Wie kann ich dir helfen?",
    "Wie geht es dir?": "Mir geht es gut, danke der Nachfrage!",
    "Was kannst du?": "Ich kann dir einfache Fragen beantworten."
  };
  return responses[message] || "Tut mir leid, ich verstehe dich nicht.";
}
