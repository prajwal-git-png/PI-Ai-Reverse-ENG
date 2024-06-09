document.getElementById('submit-btn').addEventListener('click', async function() {
    const userInput = document.getElementById('userInput').value;
    const chatLog = document.getElementById('chat-history');

    if (userInput.trim() === "") {
        return;
    }

    chatLog.innerHTML += `<div class="user-message">${userInput}</div>`;
    document.getElementById('userInput').value = "";

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: userInput }),
        });

        const data = await response.json();
        chatLog.innerHTML += `<div class="bot-message">${data.response}</div>`;
        chatLog.scrollTop = chatLog.scrollHeight;
    } catch (error) {
        console.error('Error:', error);
        chatLog.innerHTML += `<div class="bot-message">An error occurred. Please try again.</div>`;
    }
});



