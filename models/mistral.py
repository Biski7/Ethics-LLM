from transformers import AutoTokenizer, AutoModelForCausalLM
import torch, requests

def query_mistral(prompt):
    """
    Query the Mistral model with a given prompt. 
    """
    model_name = "mistralai/Mistral-7B-v0.1" 
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Preparing our input using the prompt from the dataset 
    inputs = tokenizer(prompt, return_tensors="pt")

    # Generating the response with default parameters. Will need to fiddle with this later. 
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            # max_length=400,
            num_return_sequences=1,
            # temperature=0.7,
        )

    # Decoding the output response
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extracting the judgment score 
    score = None
    for line in full_response.split('\n'):
        if line.startswith("Response judgment:"):
            score = line.split(':')[1].strip()
            break
    
    # Extracting the justification from the response
    justification_parts = full_response.split('Justification:', 1)
    justification = justification_parts[1].strip() if len(justification_parts) > 1 else ''
    
    return full_response, score, justification

# For using Ollama (if you want to run Mistral locally)
def query_ollama_mistral(prompt):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False,
        "max_tokens": 1000
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        full_response = result['response']
        score = None
        justification = ""
        lines = full_response.split('\n')
        for index, line in enumerate(lines):
            line = line.strip()
            if line.startswith("Response judgment:"):
                score = line.split(':', 1)[1].strip()
                justification = '\n'.join(line.strip() for line in lines[index+1:]).strip()
                break
        return full_response, score, justification
    else:
        return f"Error: {response.status_code}", None, None