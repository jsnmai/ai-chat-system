// ============================================================
// AI Chat — JavaScript
// Handles sending messages to the backend and displaying
// the conversation in the browser.
// ============================================================


// --- Element references -------------------------------------
// Grab the HTML elements once at the top so we can reuse them
// without searching the DOM on every message.
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const roleInput = document.getElementById("role-input");
const sendBtn = document.getElementById("send-btn");


// --- appendMessage ------------------------------------------
// Creates a message bubble and appends it to the chat box.
// role: "user" or "ai" — determines bubble color and alignment via CSS.
function appendMessage(role, text) {
    const div = document.createElement("div");
    div.classList.add("message", role);  // e.g. "message user" or "message ai"
    div.textContent = text;
    chatBox.appendChild(div);

    // Scroll to the bottom so the newest message is always visible.
    chatBox.scrollTop = chatBox.scrollHeight;
}


// --- sendMessage --------------------------------------------
// Reads the input field, shows the user's message, sends it
// to the /chat endpoint, then displays the AI's reply.
async function sendMessage() {
    const message = userInput.value.trim();  // trim() strips leading/trailing whitespace

    // Ignore empty submissions.
    if (!message) return;

    appendMessage("user", message);
    userInput.value = "";

    // Require a role before sending — show an error message if missing.
    const role = roleInput.value.trim();
    if (!role) {
        appendMessage("ai", "Please enter a role for the assistant before sending a message.");
        return;
    }

    // POST the message and role to the backend as JSON.
    // async/await means the browser waits for the response without freezing the page.
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },  // tell the server we're sending JSON
            body: JSON.stringify({ message: message, role: role }),  // convert JS object to JSON string
        });

        const data = await response.json();

        // If the server returned an error, show the error message instead of a reply.
        if (!response.ok) {
            appendMessage("ai", data.detail || "Something went wrong. Please try again.");
            return;
        }

        appendMessage("ai", data.reply || "No response received.");
    } catch (error) {
        appendMessage("ai", "Could not reach the server. Please check your connection.");
    }
}


// --- Event listeners ----------------------------------------

// Send on button click.
sendBtn.addEventListener("click", sendMessage);

// Send on Enter key so the user doesn't have to reach for the mouse.
userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
