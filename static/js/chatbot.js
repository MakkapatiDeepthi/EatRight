document.addEventListener("DOMContentLoaded", function() {
    console.log("Chatbot script loaded!");

    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-box");

    function addMessage(content, className) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(className);
        messageDiv.innerText = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendBtn.addEventListener("click", function(event) {
        event.preventDefault();
        const message = userInput.value.trim();
        if (message === "") return;

        console.log("Sending message to server:", message);
        addMessage(`You: ${message}`, "user-message");
        userInput.value = "";

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received response from server:", data);
            if (data.response) {
                addMessage(`Bot: ${data.response}`, "bot-message");
            } else {
                addMessage("Bot: Sorry, I didn't get a proper response.", "bot-message");
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage("Bot: Error connecting to chatbot.", "bot-message");
        });
    });

    function showLoadingIndicator() {
        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("loading-indicator");
        loadingDiv.innerText = "Bot is typing...";
        chatMessages.appendChild(loadingDiv);
    }
    
    function hideLoadingIndicator() {
        const loadingDiv = document.querySelector(".loading-indicator");
        if (loadingDiv) loadingDiv.remove();
    }
    
    userInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            sendBtn.click();
        }
    });
});
