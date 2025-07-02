from transformers import RobertaForSequenceClassification, RobertaTokenizer
import torch 

def query_roberta_large(prompt, model_name="roberta-large", num_labels=2):
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

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
    
    # Sending empty values just for consistency with other models and our output
    full_response = " "
    justification = " "
    # Return the prediction (0 or 1)
    score = str(predicted_class)
    # print(f"The predicted class is {str(predicted_class)}")

    return full_response, score, justification
