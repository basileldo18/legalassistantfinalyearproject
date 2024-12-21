import React, { useState } from 'react';
import axios from 'axios';  // Import Axios

function Chatbot() {
  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState([]);  // Store chat messages

  const handleMessageChange = (e) => {
    setUserMessage(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Add the user's message to the chat
    const newMessages = [...messages, { sender: 'user', text: userMessage }];
    setMessages(newMessages);  // Update the messages state

    try {
      // Send POST request using Axios
      const response = await axios.post('http://localhost:5000/process_chat', {
        userMessage: userMessage,
      });

      // Add the bot's reply to the chat
      setMessages([...newMessages, { sender: 'bot', text: response.data.reply }]);
    } catch (error) {
      console.error("Error sending message:", error);
    }

    // Clear the input field after sending the message
    setUserMessage("");
  };

  return (
    <div>
      <h1>Chatbot</h1>
      
      {/* Display the conversation */}
      <div className="chat-box" style={{ maxHeight: '400px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: '10px' }}>
            <strong>{msg.sender === 'user' ? 'You' : 'Bot'}:</strong>
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      
      {/* User input form */}
      <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
        <input 
          type="text" 
          value={userMessage} 
          onChange={handleMessageChange} 
          placeholder="Ask a question..." 
          style={{ width: '80%', padding: '10px' }}
        />
        <button type="submit" style={{ padding: '10px 15px' }}>Send</button>
      </form>
    </div>
  );
}

export default Chatbot;
