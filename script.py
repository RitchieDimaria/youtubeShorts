
from openai import OpenAI

def gen_interesting_fact():
    client = OpenAI(api_key='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')


    response = client.completions.create(
        model="text-davinci-003",
        prompt="Tell me an interesting fact in a small paragraph",
        max_tokens=240)

    # Access the generated response
    generated_text = response.choices[0].text
    print(generated_text)


