import io
import json
import os
import threading

import firebase_admin
import requests
import base64
from fpdf import FPDF
from flask import Flask, logging, render_template, request, send_file, session, redirect, url_for, jsonify
from firebase_admin import auth, initialize_app, credentials, db
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
import mysql.connector

# Establish a connection
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Basileldo',
        database='advocate_db'
    )
    if conn.is_connected():
        print("Connection to MySQL database established successfully!")
        
    cursor = conn.cursor(dictionary=True)
    print("Cursor created:", cursor)
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
# Initialize Firebase Admin SDK
try:
    # Initialize Firebase Admin SDK with service account credentials
    cred = credentials.Certificate(r'templates/firebaseconfig.json')  # Path to your service account key file
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully!")
except Exception as e:
    logging.error("Failed to initialize Firebase Admin SDK")
    logging.error(f"Error details: {str(e)}")
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

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    user_id = session.get('user_id')
    username = session.get('username') 
    print(username) # Get the user_id from the session
    if user_id:
        return jsonify({'user_id': user_id,'username':username})

    else:
        return jsonify({'message': 'User not logged in'}), 401

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
    
    # Step 2: Prepare the document type based on the input
    document_type = "lease"  # Default type, can adjust based on input
    if "copyright" in lease_details.lower():
        document_type = "copyright"
    elif "contract" in lease_details.lower():
        document_type = "contract"

    # Step 3: Prepare the prompt for the Llama model based on the document type
    if document_type == "lease":
        prompt = f"""
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
        prompt = f"""
        Given the following copyright agreement details paragraph:

        {lease_details}

        Extract the relevant information and structure it into a JSON object with the following attributes:
        - Effective Date (DD/MM/YYYY format)
        - Author Information (Name, Parent's Name, Age, Address)
        - Publisher Information (Name, Parent's Name, Age, Address)
        - Copyright Details (Work Title, Work Type, Copyright Registration Number, Copyright Duration)
        - License Terms (Licensing Scope, Royalty Percentage, Payment Schedule)
        - Other Clauses (Exclusivity, Termination Conditions, Territory)

        Each attribute should be filled with the corresponding value from the paragraph.
        If any attribute is missing, leave it blank. The output should be a well-structured JSON object based on these attributes.
        """
    
    else:
        return jsonify({'error': 'Unknown document type'}), 400

    # Step 4: Send the request to the Llama model for analysis
    print("Step 2: Sending request to Llama model for analysis.")
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[ 
            {"role": "system", "content": """
            You are a highly accurate legal content extractor. Your task is to extract detailed information from the provided legal agreements. Follow these instructions:
            1. *Data Extraction*: Extract the following fields based on the document type:
                - For Lease Agreement: Effective Date, Lessor Information (Name, Parent's Name, Age, Address), Lessee Information (Name, Parent's Name, Age, Address), Property Details (Property Number, Total Area, Property Location), Lease Terms (Term Duration, Monthly Lease Amount, Security Deposit, Payment Due Date), Other Clauses (Late Charges, Conditions for Security Deposit, Termination Notice Period)
                - For Copyright Agreement: Effective Date, Author Information (Name, Parent's Name, Age, Address), Publisher Information (Name, Parent's Name, Age, Address), Copyright Details (Work Title, Work Type, Copyright Registration Number, Copyright Duration), License Terms (Licensing Scope, Royalty Percentage, Payment Schedule), Other Clauses (Exclusivity, Termination Conditions, Territory)

            2. *Handling Missing Information*: If any information is missing, mark it as 'Not provided'.
            3. *Ensure Exact Matches*: Match the data exactly as it is presented in the input. Do not infer or guess information.
            4. *Formatting*: Output the extracted information in the following **exact JSON format**:
            {
                "Effective_Date": "DD/MM/YYYY",
                "Author_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
                "Publisher_Information": {"Name": "Name", "Parents_Name": "Name", "Age": "Age", "Address": "Address"},
                "Copyright_Details": {"Work_Title": "Title", "Work_Type": "Type", "Copyright_Registration_Number": "Registration Number", "Copyright_Duration": "Duration"},
                "License_Terms": {"Licensing_Scope": "Scope", "Royalty_Percentage": "Percentage", "Payment_Schedule": "Schedule"},
                "Other_Clauses": {"Exclusivity": "Exclusivity", "Termination_Conditions": "Conditions", "Territory": "Territory"}
            }

            5. *Quality Assurance*: Ensure that all fields are filled accurately and completely. If a piece of information is not found in the text, return 'Not provided'.
            """},
            {"role": "user", "content": prompt}
        ],
        temperature=0.001,
        max_tokens=1024,
        top_p=1,
        stream=False,
        response_format={"type": "json_object"}
    )

    # Step 5: Collect the response from the model
    bot_reply = completion.choices[0].message.content
    extracted_data = ""
    try:
        extracted_data = json.loads(bot_reply)  # Attempt to parse JSON response
        print("JSON generated successfully.")
    except json.JSONDecodeError as e:
        return jsonify({'error': 'Failed to parse JSON response', 'details': str(e)}), 500
    print(extracted_data)
    print(document_type)
    # Step 6: Return the JSON response
    if document_type == "lease":
        return render_template('ss.html', data=extracted_data)
    elif document_type == "copyright":
        return render_template('ss1.html', data=extracted_data)


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

@app.route('/advocates')
def advo():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('advocate.html')

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
        user_id = session.get('user_id')
        print(user_id)
        print(user_message)
        if user_message:
                prompt = f"""
Act as an advanced AI legal assistant specializing in Indian law. A user is seeking legal guidance on the following scenario: {user_message}. Your role is to provide a clear, detailed, and step-by-step response, ensuring the advice is actionable, accurate, and user-specific. 

Structure your response as follows:
1. **Understanding the Issue**: Briefly summarize the user's query and highlight the key legal aspects involved.
2. **Legal Context and Provisions**: Explain the relevant Indian legal provisions, acts, rights, and obligations associated with the scenario. Include any notable precedents or case laws, if applicable.
3. **Step-by-Step Guidance**: Provide a structured plan of action the user should follow, ensuring each step is easy to understand and practical to implement.
4. **Potential Outcomes and Risks**: Outline possible outcomes, legal implications, and any risks or consequences the user should be aware of.
5. **Edge Cases and Exceptions**: Consider common edge cases, complications, or exceptions related to the query. Offer specific advice for handling these scenarios.
6. **Practical Advice and Tips**: Share practical tips, best practices, and strategies for navigating the legal process effectively.

Additional Guidelines:
- Use clear and concise language suitable for users with limited legal knowledge.
- Avoid ambiguity or overly technical jargon unless necessary, and explain terms where required.
- Include a note to consult a qualified legal professional for personalized and binding advice.

Ensure the response is comprehensive and addresses the user's query holistically, empowering them to take informed actions with confidence.
"""

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
                print(formatted_reply)
                return jsonify({"reply": formatted_reply, "user_id": user_id})
            
        return jsonify({"reply": "Sorry, I couldn't understand your message."})
@app.template_filter('is_dict')
def is_dict(value):
    return isinstance(value, dict)

@app.route('/select_advocate', methods=['GET', 'POST'])
def select_advocate():
    if request.method == 'POST':
        category = request.form.get('category')
        location = request.form.get('location').strip()
        min_experience = request.form.get('min_experience', 0)
        min_rating = request.form.get('min_rating', 0)
        
        # Debug prints
        print(f"Category: {category}")
        print(f"Location: {location}")
        print(f"Min Experience: {min_experience}")
        print(f"Min Rating: {min_rating}")

        # Convert inputs to proper types
        try:
            min_experience = int(min_experience)
            min_rating = float(min_rating)
        except ValueError:
            return "Invalid input for experience or rating", 400

        # Debug: print the formatted query parameters
        print(f"Formatted Params: category={category}, location={location}, experience={min_experience}, rating={min_rating}")
        
        # Query to filter advocates by category, location, experience, and rating
        query = """
        SELECT * FROM advocates
        WHERE category = %s
        AND location LIKE %s
        AND experience >= %s
        AND rating >= %s
        ORDER BY rating DESC
        """
        params = (category, f"%{location}%", min_experience, min_rating)
        
        # Debug: print the SQL query
        print(f"SQL Query: {query}")
        print(f"Params: {params}")
        
        # Execute query
        cursor.execute(query, params)
        result = cursor.fetchall()
        
        # Debug: Check the result
        print(f"Query Result: {result}")
        
        if result:
            return render_template('advocate_results.html', advocates=result)
        else:
            message = "No advocates found with the given criteria."
            return render_template('advocate.html', message=message)

    return render_template('advocate_filter_form.html')

# Register the filter with the Jinja environment
app.jinja_env.filters['is_dict'] = is_dict
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)