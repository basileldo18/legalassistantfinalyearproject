import React from "react";
import "./main.css"; // Optional: Add a CSS file for styling

function MainPage() {
  const handleGetStarted = () => {
    // Scroll to the operations section
    document.getElementById("operations-section").scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="main-page">
      <div className="navbar">
        <img
          src={`${process.env.PUBLIC_URL}/logo.svg`}
          alt="Logo"
          className="logo"
        />
        <h1>AI LEGAL ASSISTANT</h1>
      </div>

      <div className="content">
        <div className="description">
          <h2>What is AI Legal Assistant?</h2>
          <p>
            The AI Legal Assistant helps individuals and small businesses with
            legal guidance, drafting documents, and navigating the legal process
            with ease. It uses advanced AI technology to simplify complex legal
            tasks, making legal services more accessible and efficient.
          </p>
          <div className="get-started">
            <button className="btn-start" onClick={handleGetStarted}>
              Get Started
            </button>
          </div>
        </div>
        <div className="image">
          <img
            src={`${process.env.PUBLIC_URL}/legal.webp`} // Replace with your image path
            alt="Legal Assistant"
            className="legal-image"
          />
        </div>
      </div>

      {/* Operations Section */}
      <div id="operations-section" className="operations">
        <h2>Operations You Can Perform</h2>
        <div className="operation-list">
          <div className="operation-item">
            <h3>Chatbot</h3>
            <button className="btn-navigate" onClick={() => window.location.href = '/chatbot'}>Go to Chatbot</button>
          </div>
          <div className="operation-item">
            <h3>Document Generation</h3>
            <button className="btn-navigate" onClick={() => window.location.href = '/document'}>Go to Document Generation</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MainPage;
