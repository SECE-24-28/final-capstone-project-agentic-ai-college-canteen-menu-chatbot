const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

function addMessage(text, sender = "bot") {
  const message = document.createElement("div");
  message.className = `message ${sender}`;
  message.textContent = text;
  chatLog.appendChild(message);
  chatLog.scrollTop = chatLog.scrollHeight;
  return message;
}

async function askBot(question) {
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: question }),
  });
  const data = await response.json();
  return data.response || "I could not prepare a reply right now.";
}

async function handleQuestion(question) {
  const cleanQuestion = question.trim();
  if (!cleanQuestion) return;

  addMessage(cleanQuestion, "user");
  chatInput.value = "";
  sendBtn.disabled = true;
  const waitingMessage = addMessage("Checking the weekly hostel menu...");

  try {
    waitingMessage.textContent = await askBot(cleanQuestion);
  } catch (error) {
    waitingMessage.textContent = "The server is not responding. Please check that Flask is running and try again.";
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  handleQuestion(chatInput.value);
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => handleQuestion(button.dataset.prompt));
});

addMessage("Hi! Ask me things like: Is chapati available on Monday? What is Friday dinner? What food is available today?");
