from ai_brain import route_request, ask_openai, VALID_FUNCTIONS
import functions

user_request = input("Enter your request: ")
result = route_request(user_request)
print(result)

if result in VALID_FUNCTIONS:
    print(functions.read_file(result))
else:
    print(ask_openai(user_request + "Give me a short and straight to the point answer."))