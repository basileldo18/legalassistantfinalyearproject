import React, { useState } from "react";
import "./chatbot.css"; // Import the CSS for styling

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");

  const handleUserInput = (e) => {
    setUserInput(e.target.value);
  };

  const handleSendMessage = () => {
    if (userInput.trim()) {
      const newMessage = { text: userInput, sender: "user" };
      setMessages([...messages, newMessage]);
      setUserInput("");

      // Simulate a response from the chatbot
      setTimeout(() => {
        const botMessage = { text: "This is a bot response.", sender: "bot" };
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      }, 1000);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbox">
        <div className="messages">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
            >
              <p>{msg.text}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="input-section">
        <textarea
          value={userInput}
          onChange={handleUserInput}
          placeholder="Type a message..."
          className="input-box"
        />
        <button onClick={handleSendMessage} className="send-button">Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
