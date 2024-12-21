import React, { useState } from 'react';

const LeaseForm = () => {
  const [leaseDetails, setLeaseDetails] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [responseMessage, setResponseMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!leaseDetails) {
      setErrorMessage('Please enter lease details before submitting.');
      return;
    }

    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:5000/generate_pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',  // Send JSON
        },
        body: JSON.stringify({
          lease_details: leaseDetails,  // Send lease details as JSON
        }),
      });

      if (response.ok) {
        const htmlContent = await response.text();  // Get HTML as text
        setResponseMessage(htmlContent);  // Set the HTML as response
      } else {
        const errorData = await response.json();
        setResponseMessage('Error: ' + errorData.error);
      }
    } catch (error) {
      setResponseMessage('Network error: ' + error.message);
    }
  };

  return (
    <div className="container">
      <form onSubmit={handleSubmit}>
        <h2>Lease Agreement Generator</h2>
        <textarea
          id="lease_details"
          value={leaseDetails}
          onChange={(e) => setLeaseDetails(e.target.value)}
          placeholder="Enter lease details..."
          required
        />
        <input type="submit" value="Generate PDF" />
      </form>

      {/* Error message */}
      <div id="error-message" className="error" style={{ display: errorMessage ? 'block' : 'none' }}>
        {errorMessage}
      </div>

      {/* Response message */}
      <div
        id="response-message"
        style={{ display: responseMessage ? 'block' : 'none' }}
        dangerouslySetInnerHTML={{ __html: responseMessage }}  // Inject the HTML content safely
      />
    </div>
  );
};

export default LeaseForm;

