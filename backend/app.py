
import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Import CORS for handling cross-origin requests
import requests  # Import requests to interact with Groq's API

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your Groq API key
GROQ_API_KEY = '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'  # Replace with your actual Groq API key

# Groq API URL (change if different for your endpoint)
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'  # Example endpoint, adjust as needed

@app.route('/process_chat', methods=['POST'])
def process_chat():
    data = request.get_json()
    user_message = data.get("userMessage")
    print(f"User message received: {user_message}")

    if user_message:
        # Constructing the dynamic legal prompt
        prompt = f"""Act as a knowledgeable legal assistant specializing in Indian law. A user is seeking legal guidance on the following scenario: {user_message}. Provide a thorough response that includes:

        - Clear steps the user should follow,
        - Relevant legal provisions, rights, and obligations,
        - Potential outcomes or consequences,
        - Practical advice for navigating the situation,
        - Consideration of any common edge cases or complications related to the scenario.
        
        Present each step and action point in a structured, easy-to-follow format, ensuring that the response is actionable and relevant to the user’s specific needs."""

        try:
            # Send the dynamic prompt to the Groq model using their API
            response = requests.post(
                GROQ_API_URL,
                headers={'Authorization': f'Bearer {GROQ_API_KEY}'},
                json={
                    'model': 'llama3-8b-8192',  # Replace with your actual model name
                    'messages': [
                        {"role": "system", "content": "Act as a legal assistant specializing in Indian law."},
                        {"role": "user", "content": prompt}
                    ],
                    'temperature': 1,
                    'max_tokens': 1024,
                    'top_p': 1
                }
            )

            # Handle the API response
            if response.status_code == 200:
                bot_reply = response.json()['choices'][0]['message']['content']

                # Format the response to be rendered as HTML
                formatted_reply = f"""
                Legal Advice for Your Scenario:
                {bot_reply.replace('\n', '<br><br>')}
                """

                # Send the response back to the frontend
                return jsonify({"reply": formatted_reply})
            else:
                # Handle unsuccessful API call
                print(f"Error from Groq API: {response.status_code} - {response.text}")
                return jsonify({"reply": "Sorry, there was an error processing your request. Please try again."})

        except Exception as e:
            # Handle any other errors
            print(f"Error processing request: {e}")
            return jsonify({"reply": "Sorry, there was an error processing your request. Please try again."})

    return jsonify({"reply": "Sorry, I couldn't understand your message."})
from groq import Groq
os.environ["GROQ_API_KEY"] = "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"

client = Groq()
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Step 1: Receive lease details from the request
    lease_details = request.get_json().get('lease_details')

    print(lease_details)
    if not lease_details:
        return jsonify({'error': 'Lease details are required!'}), 400
                # Step 2: Prepare the prompt for the Llama model
    document_type = "lease" # Default type, you can adjust this logic based on the input
    if "copyright" in lease_details.lower():
            document_type = "copyright"
    elif "contract" in lease_details.lower():
            document_type = "contract"

        # Step 3: Prepare the prompt for the Llama model based on the document type
    if document_type == "lease":
          prompt =f"""
Given the following lease details paragraph:

{lease_details}

Extract the information and structure it into a JSON object with these attributes:
- Effective Date (DD/MM/YYYY format)
- Lessor Information (Name, Parent's Name, Age, Address)
- Lessee Information (Name, Parent's Name, Age, Address)
- Property Details (Property Number, Total Area, Property Location)
- Lease Terms (Term Duration, Monthly Lease Amount, Security Deposit, Payment Due Date)
- Other Clauses (Late Charges, Conditions for Security Deposit, Termination Notice Period)

Each attribute should be filled with the corresponding value from the paragraph, or left blank if not found.
The output should be a well-structured JSON object based on these attributes.
"""



    elif document_type == "copyright":
            prompt = """
            Generate a JSON object representing a Copyright Agreement based on the following details:
            {
            "Grantor_Information": {
                "Name": "[Full name of the grantor]",
                "Parents_Name": "[Father’s name]",
                "Age": "[Age in years]",
                "Address": "[Residential address]"
            },
            "Grantee_Information": {
                "Name": "[Full name of the grantee]",
                "Parents_Name": "[Father’s name]",
                "Age": "[Age in years]",
                "Address": "[Residential address]"
            },
            "Work_Details": {
                "Work_Title": "[Title of the copyrighted work]",
                "Work_Type": "[Type of the copyrighted work]",
                "Work_Description": "[Description of the work]"
            },
            "License_Terms": {
                "License_Type": "[Type of license granted]",
                "License_Purpose": "[Purpose of use]",
                "Territory": "[Territory covered by the license]",
                "Duration": "[License duration]"
            },
            "Financial_Terms": {
                "Royalty_Agreement": {
                "Amount": "[Amount in figures]",
                "In_Words": "[Amount in words]"
                },
                "Late_Charges": "[Amount for late payment]"
            },
            "Termination": {
                "Notice_Period": "[Notice period for termination]",
                "Conditions": "[Conditions for termination]"
            }
            }

            this is the input from the user{lease_details}
            """
    else:
            return jsonify({'error': 'Unknown document type'}), 400


            # Step 3: Send the request to the Llama model for case analysis
                # Step 3: Send the request to the Llama model for case analysis
    print("Step 2: Sending request to Llama model for analysis.")
    completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
   {"role": "system", "content": """
You are a highly accurate legal content extractor. Your task is to extract detailed information from the provided Lease Agreement. Follow these instructions:
1. **Data Extraction**: Extract the following fields from the provided text:
   - **Effective Date**
   - **Lessor Information** (Name, Parents' Name, Age, Address)
   - **Lessee Information** (Name, Parents' Name, Age, Address)
   - **Property Details** (Property Number, Total Area, Property Location)
   - **Lease Terms** (Term Duration, Monthly Lease Amount, Security Deposit, Payment Due Date)
   - **Other Clauses** (Late Charges, Conditions for Security Deposit, Termination Notice Period)

2. **Handling Missing Information**: If any information is missing, mark it as **'Not provided'**.

3. **Ensure Exact Matches**: Match the data exactly as it is presented in the input. Do not infer or guess information.

4. **Formatting**: Output the extracted information in the following **exact JSON format**:
   {
      "Effective_Date": "DD/MM/YYYY",
      "Lessor_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
      "Lessee_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
      "Property_Details": {"Property_Number": "Number", "Total_Area": "Area", "Property_Location": {"Address": "Address", "City": "City", "State": "State", "Country": "Country", "Pin_Code": "PinCode"}},
      "Lease_Terms": {"Term_Duration": "Duration", "Monthly_Lease_Amount": {"Amount": "Amount", "In_Words": "Words"}, "Security_Deposit": {"Amount": "Amount", "In_Words": "Words"}, "Payment_Due_Date": "Due Date"},
      "Other_Clauses": {"Late_Charges": "Late Charges", "Conditions_for_Security_Deposit": {"Refund_Terms": "Terms", "Deductions_for_Damages": "Damages", "Cleaning": "Cleaning"}, "Termination_Notice_Period": "Notice Period"}
   }

5. **Quality Assurance**: Ensure that all fields are filled accurately and completely. If a piece of information is not found in the text, return 'Not provided'.
"""}
,
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.001,
                    max_tokens=1024,
                    top_p=1,
                    stream=False,
                    response_format={"type": "json_object"}
                )

                # Collect the response from the model
    bot_reply = completion.choices[0].message.content
    lease_json=""
    try:
                lease_json = json.loads(bot_reply) # Attempt to parse JSON response
                print("Lease JSON generated successfully.")
    except json.JSONDecodeError as e:
                return jsonify({'error': 'Failed to parse JSON response', 'details': str(e)}), 500
    print(lease_json)
    return render_template('ss.html', data=lease_json)            # Step 5: Return the JSON response
   
if __name__ == '__main__':
    app.run(debug=True)
