import google.generativeai as genai

# Configure the API key (if you haven't set it as an environment variable)
# genai.configure(api_key="YOUR_API_KEY")

# Initialize the generative model
model = genai.GenerativeModel('gemini-2.5-flash')

# Generate content from a text prompt
prompt = "Give me stock symbol of Microsoft"
response = model.generate_content(prompt)

# Print the generated text
print(response.text)