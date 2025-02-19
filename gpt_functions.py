import openai
import json
import requests
openai.api_key = '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'

def summarize_incidents(text):
    """Send text to OpenAI API for summarization."""
    
    
    prompt = [{"role":"user","content":f"Summarize, in 3 or fewer bullets, each fewer than 50 words the types of incidents being described in the text, including the underlying causes {text}"}]
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=prompt,
        max_tokens=150
    )


    return response.choices[0].message.content

def summarize_products(text):
    """Send text to OpenAI API for summarization."""
    
    
    prompt = [{"role":"user","content":f"For each row in this list, return the category of product mentioned, and keep the results consistent so that a similar type of product gets the same label. Return only a colon seperated list of the identified categories{text}"}]
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=prompt,
        max_tokens=150
    )


    return list(set(response.choices[0].message.content.split(":")))


if __name__ == "__main__":
    api_key = "your_openai_api_key_here"  # Replace with your OpenAI API key
    text_to_summarize = "Artificial intelligence is transforming the world by enabling machines to mimic human intelligence. It is widely used in healthcare, finance, transportation, and many other fields. The advancements in deep learning and neural networks have made AI more powerful and efficient."
    
    summary = summarize_text(text_to_summarize, api_key)
    print("Summary:", summary)
