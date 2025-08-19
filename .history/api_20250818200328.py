from decouple import config

# The name of your environment variable
api_key_name = 'GOOGLE_API_KAY'

# Use the config() function to get the value
try:
    api_key = config(api_key_name)
    print("Successfully retrieved the API key.")
    # You can now use the 'api_key' variable in your code.
    print(f"API Key: {api_key}")
    
except KeyError:
    print(f"Error: The environment variable '{api_key_name}' is not set.")