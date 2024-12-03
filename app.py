import io
import json
import os
import threading
import requests
import base64
from fpdf import FPDF
from flask import Flask, render_template, request, send_file, session, redirect, url_for, jsonify
from firebase_admin import auth, initialize_app, credentials
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import asyncio
import openai
from concurrent.futures import ThreadPoolExecutor
import spacy

# Initialize Firebase Admin SDK
cred = credentials.Certificate('templates/firebaseconfig.json')
initialize_app(cred)
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize model and prompt
template = """
You are an AI Legal Assistant specializing in Indian law. Use clear, concise, and structured language to provide accurate legal advice tailored to the scenario. 

Here is the conversation history: {context}

Question: {question}

Provide a step-by-step response, including:
1. A brief overview of the legal context or relevant laws applicable in India.
2. Key legal steps or actions the user should take, with examples or explanations as needed.
3. Any relevant legal documents, authorities, or organizations involved.
4. Common pitfalls, rights, or protections that may apply.
5. A summary of next steps, including any potential outcomes or additional advice if required.
"""
model = OllamaLLM(model="llama3.1")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# Greeting responses
greeting_responses = {
    "hi": "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hello": "Hi there! I provide legal assistance specific to India. What do you need help with?",
    "how are you": "I'm here to assist you with legal information in India!",
    "hey": "Hey! What legal information do you need regarding Indian laws?",
    "can you help": "Absolutely! Please describe your legal issue, and I'll provide the best advice based on Indian law.",
    "hii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hiiii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "how are you" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hiiiiii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hai" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "haii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?",
    "hiii" : "Hello! I am your AI Legal Assistant. How can I assist you with legal information today?"
}

async def stream_response(context: str, question: str):
    result = chain.invoke({"context": context, "question": question})
    for char in result:
        yield char
        await asyncio.sleep(0.02)  # Adjust this delay as needed

@socketio.on('message')
def handle_message(data):
    user_input = data.get("question", "").strip()
    context = data.get("context", "")

    # Check for greetings
    response = greeting_responses.get(user_input.lower())
    if response:
        emit('response', {"answer": response, "updated_context": context, "finished": True})
    else:
        # Stream the response
        def stream():
            for char in chain.invoke({"context": context, "question": user_input}):
                socketio.emit('response', {"answer": char, "updated_context": context, "finished": False})
                socketio.sleep(0.02)  # Adjust this delay as needed
            socketio.emit('response', {"answer": "", "updated_context": context, "finished": True})

        socketio.start_background_task(stream)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json.get('email')
        try:
            user = auth.get_user_by_email(email)
            session['username'] = email
            return jsonify({'message': 'Login successful'})
        except Exception as e:
            print("Error logging in:", e)
            return jsonify({'message': 'Login failed'}), 401
    else:
        if not session.get('username'):
            return render_template('chatadvice.html')
        return redirect(url_for('chatadvice.html'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    address = data.get('address')
    pincode = data.get('pincode')
    
    try:
        user = auth.create_user(email=email, password=password, display_name=username)
        return jsonify({'message': 'User created successfully'}), 200
    except Exception as e:
        print("Error creating user:", e)
        return jsonify({'message': 'Failed to create user'}), 400



from groq import Groq
os.environ["GROQ_API_KEY"] = "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"

client = Groq()
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Step 1: Receive lease details from the request
    lease_details = request.form.get('lease_details')
    print(lease_details)
    if not lease_details:
        return jsonify({'error': 'Lease details are required!'}), 400
                # Step 2: Prepare the prompt for the Llama model
    document_type = "lease"  # Default type, you can adjust this logic based on the input
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
1. *Data Extraction*: Extract the following fields from the provided text:
   - *Effective Date*
   - *Lessor Information* (Name, Parents' Name, Age, Address)
   - *Lessee Information* (Name, Parents' Name, Age, Address)
   - *Property Details* (Property Number, Total Area, Property Location)
   - *Lease Terms* (Term Duration, Monthly Lease Amount, Security Deposit, Payment Due Date)
   - *Other Clauses* (Late Charges, Conditions for Security Deposit, Termination Notice Period)

2. *Handling Missing Information: If any information is missing, mark it as *'Not provided'**.

3. *Ensure Exact Matches*: Match the data exactly as it is presented in the input. Do not infer or guess information.

4. *Formatting: Output the extracted information in the following **exact JSON format*:
   {
      "Effective_Date": "DD/MM/YYYY",
      "Lessor_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
      "Lessee_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
      "Property_Details": {"Property_Number": "Number", "Total_Area": "Area", "Property_Location": {"Address": "Address", "City": "City", "State": "State", "Country": "Country", "Pin_Code": "PinCode"}},
      "Lease_Terms": {"Term_Duration": "Duration", "Monthly_Lease_Amount": {"Amount": "Amount", "In_Words": "Words"}, "Security_Deposit": {"Amount": "Amount", "In_Words": "Words"}, "Payment_Due_Date": "Due Date"},
      "Other_Clauses": {"Late_Charges": "Late Charges", "Conditions_for_Security_Deposit": {"Refund_Terms": "Terms", "Deductions_for_Damages": "Damages", "Cleaning": "Cleaning"}, "Termination_Notice_Period": "Notice Period"}
   }

5. *Quality Assurance*: Ensure that all fields are filled accurately and completely. If a piece of information is not found in the text, return 'Not provided'.
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
                lease_json = json.loads(bot_reply)  # Attempt to parse JSON response
                print("Lease JSON generated successfully.")
    except json.JSONDecodeError as e:
                return jsonify({'error': 'Failed to parse JSON response', 'details': str(e)}), 500
    print(lease_json)
            # Step 5: Return the JSON response
    if document_type == "lease":
        return render_template('ss.html', data=lease_json)
    else:
        return render_template('ss1.html', data=lease_json)

@app.route('/case', methods=['POST', 'GET'])
def case_input():
    if request.method == 'POST':
        case_scenario = request.form.get('case_scenario')
        # Add your case processing logic here
        return render_template('docgeneration.html', scenario=case_scenario)
    return render_template('docgeneration.html')

# Main routes
@app.route('/')
def index():
    return render_template('authenti.html')

@app.route('/main')
def main():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('main.html')

@app.route('/bot')
def bot():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('chatadvice.html')

# Error handlers

# Process chat route (if needed for non-WebSocket fallback)
@app.route('/process_chat', methods=['POST'])
def process_chat():
        data = request.get_json()
        user_message = data.get("userMessage")
        print(user_message)
        if user_message:
                prompt = f"""Act as a knowledgeable legal assistant specializing in Indian law. A user is seeking legal guidance on the following scenario: {user_message}. Provide a thorough response that includes:

Clear steps the user should follow,
Relevant legal provisions, rights, and obligations,
Potential outcomes or consequences,
Practical advice for navigating the situation,
Consideration of any common edge cases or complications related to the scenario.
Present each step and action point in a structured, easy-to-follow format, ensuring that the response is actionable and relevant to the user’s specific needs."""

                # Send the dynamic prompt to the model
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[ 
                        {"role": "system", "content": "Act as a legal assistant specializing in Indian law."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1,
                    max_tokens=1024,
                    top_p=1,
                    stream=True,
                    stop=None,
                )

                bot_reply = ""
                for chunk in completion:
                    bot_reply += chunk.choices[0].delta.content or ""

                # Format the response to be rendered as HTML
                formatted_reply = f"""
                <b>Legal Advice for Your Scenario:</b><br><br>
                {bot_reply.replace('\n', '<br><br>')}
                """
                return jsonify({"reply": formatted_reply})
            
        return jsonify({"reply": "Sorry, I couldn't understand your message."})
@app.template_filter('is_dict')
def is_dict(value):
    return isinstance(value, dict)

# Register the filter with the Jinja environment
app.jinja_env.filters['is_dict'] = is_dict
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)