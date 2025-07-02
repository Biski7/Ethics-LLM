import csv
import os
from sklearn.metrics import accuracy_score

def calculate_accuracy(file_path):
    labels = []
    scores = []
    
    with open(file_path, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        fieldnames = csvreader.fieldnames
        
        # Identify the correct score column dynamically
        score_col = None
        for field in fieldnames:
            if field.lower() != 'label' and ('shot' in field.lower() or 'cot' in field.lower()):
                score_col = field
                break
        
        if score_col is None:
            raise ValueError(f"No score column found in {file_path}")

        for row in csvreader:
            try:
                label = int(float(row['Label']))
                score = int(float(row[score_col]))
                labels.append(label)
                scores.append(score)
            except ValueError:
                # Skip rows with bad data
                continue
    

    accuracy = accuracy_score(labels, scores)
    return accuracy

if __name__ == "__main__":
    # current_dir = os.getcwd()

    theories = ['Commonsense', 'Utilitarianism', 'Deontology', 'Virtue', 'Justice']
    theory = theories[1]

    type = 'TestHard'  # 'Test' or 'TestHard'   

    models = [ 'gemini', 'llama2', 'llama3', 'mistral']
    model = models[3]

# 'Justice'
    current_dir = f'/Users/bishalthapa/Desktop/2025/Final CAHSI Results/{theory}/TestHardNew/{model}/'

    
    files = [
            # f'{model}_{theory}_Base0-shot_{type}.csv', 
            # f'{model}_{theory}_Base1-shot_{type}.csv', 
            # f'{model}_{theory}_Base2-shot_{type}.csv', 
            # f'{model}_{theory}_Base0-shot_CoT_{type}.csv',
            # f'{model}_{theory}_Base32-shot_{type}.csv', 
            f'{model}_{theory}_Detailed0-shot_{type}.csv', 
            f'{model}_{theory}_Detailed0-shot_CoT_{type}.csv',
            f'{model}_{theory}_Detailed1-shot_{type}.csv', 
            f'{model}_{theory}_Detailed1-shot_CoT_{type}.csv',
            f'{model}_{theory}_Detailed2-shot_{type}.csv', 
            f'{model}_{theory}_Detailed2-shot_CoT_{type}.csv',
            f'{model}_{theory}_Detailed8-shot_{type}.csv', 
            f'{model}_{theory}_Detailed32-shot_{type}.csv',
        ]
    
    
    files = [os.path.join(current_dir, file) for file in files]

    for file_path in files:
        try:
            accuracy = calculate_accuracy(file_path)
            short_path = file_path[-60:]
            print(f"Type: {type}")
            print(f"Model Accuracy {short_path}: {accuracy:.2%}")
            print("" + "-" * 50)    
        except Exception as e:
            print(f"Error processing {file_path}: {e}")