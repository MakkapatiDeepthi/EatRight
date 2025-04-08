document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const chatMessages = document.getElementById("chat-messages");

    // Function to add messages to chat window
    function addMessage(content, className) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add(className);
        messageDiv.innerText = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Handle message sending
    sendBtn.addEventListener("click", function() {
        const message = userInput.value.trim();
        
        if (message === "") {
            alert("Please enter a message.");
            return;
        }
        // Add user message
        addMessage(message, "user-message");
        userInput.value = "";

        // Send request to Flask backend
        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.reply, "bot-message");
        })
        .catch(error => {
            addMessage("Error connecting to chatbot.", "bot-message");
        });
    });

    // Press Enter to Send Message
    userInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            sendBtn.click();
        }
    });
});
