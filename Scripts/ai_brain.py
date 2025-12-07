import configparser
from typing import Optional
from openai import OpenAI

# Load config values from ../config/config.ini
config = configparser.ConfigParser()
config.read('../config/config.ini')

api_key = config['openai']['api_key']
model = config['openai']['model']
temperature = float(config['openai']['temperature'])  # convert string to float

# Create OpenAI client
client = OpenAI(api_key=api_key)

def ask_openai(prompt: str) -> str:
    """
    Send a prompt to OpenAI Chat Completions API and return the reply text.
    Uses the model and temperature from config.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("OpenAI returned empty content")
    return content


VALID_FUNCTIONS = [
    "transcribe_audio",
    "query_database",
    "generate_report",
    "todo_list"
]


def route_request(user_request: str) -> str:
    """
    Routes a user request to the appropriate function name using OpenAI.
    
    Args:
        user_request: The user's input request
    
    Returns:
        The function name that best matches the request, or "none" if no match
    """
    valid_functions = VALID_FUNCTIONS
    
    functions_list = "\n".join(f"- {func}" for func in valid_functions)
    
    router_prompt = f"""You are a routing assistant inside a Python program.

I will give you a user request and a list of valid function names:
{functions_list}

Your job is to STRICTLY match the user request to ONE of these functions ONLY if it clearly fits.
For example:
- todo_list: Only if user wants to see/manage their todo list tasks

Return ONLY the single function name that EXACTLY matches the request.
No explanations, no extra text, no quotes.
If the request does NOT clearly match ANY function, return: none."""
    
    full_prompt = f"{router_prompt}\n\nUser request: {user_request}"
    return ask_openai(full_prompt)


if __name__ == "__main__":
    user_request = "whats on my todo list?"
    result = route_request(user_request)
    print(result)