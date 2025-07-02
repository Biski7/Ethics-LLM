from dotenv import load_dotenv
import os, time 
from transformers import LlamaForCausalLM, LlamaTokenizer
import torch 
import requests, json 

load_dotenv()
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")


# Through HuggingFace 
# def query_llama(prompt):
#     """
#     Query the LLaMA model with our prompt for a particular theory.
    
#     Args:
#         prompt (str): The input prompt to generate a response for.
    
#     Returns:
#         tuple: (full_response, score, justification)

#     full_response contains the overall response, score contains just 0 or 1, and justification contains the justification.
#     full_response = score + justification
#     """

#     model_name = "meta-llama/Llama-2-7b-chat-hf"  

#     try:
#         tokenizer = LlamaTokenizer.from_pretrained(model_name, use_auth_token=huggingface_api_key)
#         model = LlamaForCausalLM.from_pretrained(model_name, use_auth_token=huggingface_api_key)

        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # model = model.to(device)
        # print(f"Using device: {device}")
#     except Exception as e:
#         raise RuntimeError(f"Error loading model or tokenizer: {str(e)}")

#     # Preparing our input using the prompt from the dataset 
#     inputs = tokenizer(prompt, return_tensors="pt")

#     # Generating the response with default parameters. Will need to fiddle with this later. 
#     try:
#         with torch.no_grad():
#             outputs = model.generate(
#                 **inputs,
#                 max_length=500,
#                 num_return_sequences=1,
#                 # temperature=0.7,
#             )
#     except Exception as e:
#         raise RuntimeError(f"Error generating response: {str(e)}")

#     # Decoding the output response
#     full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     # Extracting the judgment score to store in the csv
#     # We can do this post-processing as well (easier if we do it later cause we don't know the format of the response)
#     score = None
#     justification = ""

#     for line in full_response.split('\n'):
#         if line.startswith("Response judgment:"):
#             score = line.split(':')[1].strip()
#             break
#         elif line.startswith("Justification:"):
#             justification = line.split(':', 1)[1].strip()
#             break 

#     # Extracting  the justification from the response (works for justice for now)
#     justification_parts = full_response.split('Justification:', 1)
#     justification = justification_parts[1].strip() if len(justification_parts) > 1 else ''
    
#     # Returning the actual response, score (integer part), and the justification part
#     return full_response, score, justification


# USING OLLMA or Downloading llama locally ( I think we can't use GPU acceleration here. We can do it using HuggingFace though.)
def query_ollama2(prompt):
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": "llama2",
        "prompt": prompt,
        "stream": False,
        "max_tokens": 1000
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        full_response = result['response']
        
        score = None
        # for line in full_response.split('\n'):
        #     if line.startswith("Response judgment:"):
        #         score = line.split(':')[1].strip()
        #         break
        
        # justification_parts = full_response.split('Justification:', 1)
        # justification = justification_parts[1].strip() if len(justification_parts) > 1 else ''
        
        # return full_response, score, justification

        justification = ""

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

    else:
        return f"Error: {response.status_code}", None, None


def query_ollama3(prompt):
    url = "http://localhost:11434/api/generate"
    
    data = {
        "model": "llama3",
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

    else:
        return f"Error: {response.status_code}", None, None
