import requests
from bs4 import BeautifulSoup
import json
from transformers import pipeline

# Step 1: Provide the website URL
website_url = "https://docs.netscaler.com/en-us/citrix-adc/current-release/getting-started-with-citrix-adc.html"

# Step 2: Fetch the website content using web scraping
response = requests.get(website_url)
html_content = response.text

# Step 3: Extract the text from HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")
website_text = soup.get_text()

# Step 4: Train an NLP model
nlp_model = pipeline("question-answering")
training_data = [{"context": website_text, "qas": [{"question": "What is the website about?", "id": "1"}]}]
nlp_model.train(training_data)

# Step 5: Save the trained model in JSON format
model_data = nlp_model.model.save_pretrained("trained_model")
model_config = nlp_model.model.config.to_dict()
model_data["model_config"] = model_config
with open("trained_model.json", "w") as file:
    json.dump(model_data, file)

# Step 6: Load the trained model from the JSON file
with open("trained_model.json", "r") as file:
    model_data = json.load(file)
    model = nlp_model.model_class.from_pretrained("trained_model", **model_data["model_config"])
    nlp_model.model = model

# Step 7: Answer user questions based on the trained model
user_question = "What is the website about?"
answer = nlp_model({"question": user_question, "context": website_text})
print("Answer:", answer["answer"])
print("Confidence:", answer["score"])
