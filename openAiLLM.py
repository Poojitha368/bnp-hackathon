import openai
openai.api_key = "your-api-key-here"

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! How can I use OpenAI API in Python?"}
    ]
)

print(response.choices[0].message['content'])
