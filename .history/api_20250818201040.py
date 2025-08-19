import google.generativeai as genai

# Make sure your API key is configured correctly
# genai.configure(api_key="YOUR_API_KEY")

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)