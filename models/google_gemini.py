import google.generativeai as genai
from dotenv import load_dotenv
import os, time 


def query_gemini(prompt):
    load_dotenv()
    genai.configure(api_key=os.environ["genai_key1"])

    model = genai.GenerativeModel('gemini-1.5-pro')

    response = model.generate_content(prompt)

    time.sleep(3)

    # Extract the full response
    if response.parts:
        full_response = response.parts[0].text.strip()
    else:
        full_response = ""

    # Extracting the judgment score to store in the csv
    score = None
    for line in full_response.split('\n'):
        if line.startswith("Response judgment:"):
            score = line.split(':')[1].strip()
            break
    
    # Extracting  the justification from the response
    justification_parts = full_response.split('Justification:', 1)
    justification = justification_parts[1].strip() if len(justification_parts) > 1 else ''
    
    # Returning the actual response, score (integer part), and the justification part
    return full_response, score, justification