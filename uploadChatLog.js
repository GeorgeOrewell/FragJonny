function uploadChatLog() {
  // Holen der Chat-Logs aus dem LocalStorage
  const chatLog = localStorage.getItem('chatLog') || '[]'; // Wenn kein Log existiert, wird ein leeres Array verwendet
  const chatLogBase64 = btoa(chatLog); // Base64-kodierter Inhalt der Chat-Logs
  
  // Erstelle einen Zeitstempel für den Dateinamen
  const now = new Date();
  const timestamp = now.toISOString().replace(/T/, '-').replace(/:/g, '-').split('.')[0]; // YYYY-MM-DD-HH-MM-SS
  const filePath = `LogFiles/LogFile-${timestamp}.log`;  // Dateipfad mit Zeitstempel
  
  const repoOwner = 'GeorgeOrewell';   // GitHub-Username
  const repoName = 'LogFiles';         // Repository-Name
  const branch = 'main';               // Branch, z.B. 'main' oder 'master'
  const token = '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';   // Dein GitHub Personal Access Token
  
  const commitMessage = `Add log file for ${timestamp}`;  // Commit-Nachricht
  const url = `https://api.github.com/repos/${repoOwner}/${repoName}/contents/${filePath}`;
  
  const data = {
    message: commitMessage,
    content: chatLogBase64,
    branch: branch
  };

  // API-Aufruf mit axios
  axios.put(url, data, {
    headers: {
      'Authorization': `token ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log('Chat-Log erfolgreich hochgeladen:', response.data.content.html_url);
  })
  .catch(error => {
    console.error('Fehler beim Hochladen:', error.response.data);
  });
}
