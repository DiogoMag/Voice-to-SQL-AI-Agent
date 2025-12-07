import configparser
from openai import OpenAI

# Load config values from ../config/config.ini
config = configparser.ConfigParser()
config.read('../config/config.ini')

api_key = config['openai']['api_key']
model = config['openai']['model']
temperature = float(config['openai']['temperature'])  # convert string to float

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Send a simple prompt
response = client.chat.completions.create(
    model=model,
    temperature=temperature,
    messages=[
        {"role": "user", "content": "Tell me a fun fact about space."}
    ]
)

# Print the response
print(response.choices[0].message.content)
