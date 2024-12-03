from flask import Flask, request, jsonify, render_template
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # Enables CORS

# Initialize model and prompt
template = """
You are an AI Legal Assistant specializing in Indian law. Provide clear and structured legal advice based on the scenario given. 

Here is the conversation history: {context}

Question: {question}
Answer with step-by-step legal advice and mention relevant laws in India:
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
    "can you help": "Absolutely! Please describe your legal issue, and I'll provide the best advice based on Indian law."
}
print(greeting_responses)

def process_chat(data, context):
    user_input = data.get("question", "").strip()
    context = data.get("context", "")
    print(f"Received user input: {user_input}")
    print(f"Current context: {context}")
    
    # Check for greetings and common phrases
    response = greeting_responses.get(user_input.lower())
    if response:
        print(f"Greeting detected. Responding with: {response}")
        context += f"\nUser: {user_input}\nAI: {response}"
        return {"answer": response, "updated_context": context}

    # Process the chat with the model for legal advice
    try:
        print("Invoking language model...")
        result = chain.invoke({"context": context, "question": user_input})
        print(f"Model response: {result}")
        
        if not result or result.strip() == "":
            print("Empty response from model. Using default message.")
            result = "I'm sorry, I didn't understand that. Please provide more details about your legal issue."
        
        context += f"\nUser: {user_input}\nAI: {result}"
        print(f"Updated context: {context}")
        return {"answer": result, "updated_context": context}
    except Exception as e:
        print(f"Error processing chat: {str(e)}")
        return {"answer": f"An error occurred while processing your request: {str(e)}", "updated_context": context}

# Add this test function
def test_process_chat():
    test_inputs = [
        "Hello",
        "What is a contract?",
        "Explain the basics of Indian criminal law",
        "Tell me about property rights in India"
    ]
    
    for input_text in test_inputs:
        print(f"\nTesting input: {input_text}")
        result = process_chat({"question": input_text, "context": ""}, "")
        print(f"Output: {result['answer']}")
        print("-" * 50)

# Call the test function
if __name__ == "__main__":
    test_process_chat()
# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    
    # Use a separate thread to handle the processing
    result = {}
    thread = threading.Thread(target=lambda: result.update(process_chat(data, data.get("context", ""))))
    thread.start()
    thread.join()  # Optional: wait for the thread to complete before sending the response

    return jsonify(result)

