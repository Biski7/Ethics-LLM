from transformers import BertTokenizer, BertForSequenceClassification
import torch 

def query_bert(prompt, model_name="bert-base-uncased", num_labels=2):
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

    # Encoding the input prompt
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Using GPU if available, else it will use cpu (need to install CUDA)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Make prediction
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
    
    # Return the prediction (0 or 1)
    full_response = " "
    justification = " "
    # if predicted_class == 0:
    #     score = "0"
    # else:  
    #     score = "1" 
    score = str(predicted_class)   
    # print(f"The predicted class is {str(predicted_class)}")

    return full_response, score, justification



