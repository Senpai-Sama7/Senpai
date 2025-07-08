import openai

class Planner:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_plan(self, prompt, dom_data):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{prompt}

DOM:
{dom_data}

Plan:",
            max_tokens=150
        )
        return response.choices[0].text.strip().split('
')
