import requests
import json

model = "llama3.1"
template = {
    "case_type": "",
    "ipc_sections": [],
    "applicable_laws": {
        "law_name": "",
        "sections": []
    },
    "case_sections": {
        "description": "",
        "agreement_terms": "",
        "parties_involved": []
    }
}

# Sample case study input
case_study_input = """
my name is basil eldo i ordered a product from flipkart and the recived product was differnet from orginal product i complaint flipkart customer care but they didnt respoded as mush as i need to complaint to the consumer court.
"""

prompt = f"""
Analyze the following case study and return it as JSON format with the following attributes:
- `case_type`: Type of the case (e.g., "Lease Agreement")
- `ipc_sections`: List of relevant IPC (Indian Penal Code) sections if applicable, otherwise return an empty list.
- `applicable_laws`: Include:
  - `law_name`: The name of the law applicable to the case (e.g., "Transfer of Property Act")
  - `sections`: List of relevant sections from that law
- `case_sections`: Divide the case into sections and include:
  - `description`: Brief summary of the section
  - `agreement_terms`: Specific terms agreed upon
  - `parties_involved`: Names of parties involved
  
Use the following template: {json.dumps(template)}.

Case Study: {case_study_input}
"""

data = {
    "prompt": prompt,
    "model": model,
    "format": "json",
    "stream": False,
    "options": {"temperature": 0.7, "top_p": 0.9, "top_k": 50},
}

print("Generating case study analysis...")
response = requests.post("http://localhost:11434/api/generate", json=data, stream=False)
json_data = json.loads(response.text)

# Parse and pretty-print the JSON output
print(json.dumps(json.loads(json_data["response"]), indent=2))
