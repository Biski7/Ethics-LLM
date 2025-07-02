import os
from openai import OpenAI
from dotenv import load_dotenv
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

models = ["gpt-4", "gpt-4o", "gpt-3.5-turbo"]
# We are currently not  changing any of the properties of the model i.e., using default configuration

def query_openai(prompt):
    client = OpenAI(
        api_key = os.environ.get("openai_key")
    )
    response = client.chat.completions.create(
        model=models[2],
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000
    )
    
    full_response = response.choices[0].message.content.strip()
    
    # # Extracting the judgment score to store in the csv
    # score = None
    # for line in full_response.split('\n'):
    #     if line.startswith("Response judgment:"):
    #         score = line.split(':')[1].strip()
    #         break
    
    # # Extracting  the justification from the response
    # justification_parts = full_response.split('Justification:', 1)
    # justification = justification_parts[1].strip() if len(justification_parts) > 1 else ''
    
    # # Returning the actual response, score (integer part), and the justification part
    # return full_response, score, justification

    justification = ""
    score = ""
    # Splitting the response into lines 
    lines = full_response.split('\n')

    # Processing each line
    for index, line in enumerate(lines):
        line = line.strip()  # Removing the leading/trailing whitespace 

        if line.startswith("Response judgment:"):
            score = line.split(':', 1)[1].strip()

            # Collect everything after the Response judgment line
            justification = '\n'.join(line.strip() for line in lines[index+1:]).strip()
            break  

    return full_response, score, justification

def query_gpt2(prompt, max_length=500, model_name="gpt2"):
    # Using HuggingFace
    # Load pre-trained model and tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained("openai-community/gpt2")
    model = GPT2LMHeadModel.from_pretrained("openai-community/gpt2")

    # Encode the input prompt
    input_ids = tokenizer.encode(prompt, return_tensors="pt")

    # Use GPU if available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    input_ids = input_ids.to(device)

    try:
        with torch.no_grad():
            output = model.generate(
                input_ids,
                max_length=max_length,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                temperature=0.1
            )
    except Exception as e:
        raise RuntimeError(f"Error generating response: {str(e)}")

    # Decode the generated text
    full_response = tokenizer.decode(output[0], skip_special_tokens=True)


    justification = ""
    score = ""
    # Splitting the response into lines 
    lines = full_response.split('\n')

    # Processing each line
    for index, line in enumerate(lines):
        line = line.strip()  # Removing the leading/trailing whitespace 

        if line.startswith("Response judgment:"):
            score = line.split(':', 1)[1].strip()

            # Collect everything after the Response judgment line
            justification = '\n'.join(line.strip() for line in lines[index+1:]).strip()
            break  

    return full_response, score, justification
