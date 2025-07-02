import csv
import time
import os
import pandas as pd
from models.openai_models import query_openai, query_gpt2
from models.llama import query_ollama2, query_ollama3
from models.mistral import query_mistral
from models.google_gemini import query_gemini
from models.bert import query_bert
from models.roberta import query_roberta_large
from prompts import generate_prompt
import argparse


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def load_output_dataframe(output_file):
    """Load the output CSV as a dataframe or create an empty one with the necessary columns"""
    if os.path.exists(output_file):
        try:
            return pd.read_csv(output_file)
        except pd.errors.EmptyDataError:
            # File exists but is empty
            pass
    
    # Return empty DataFrame with required columns
    return pd.DataFrame(columns=['ID', 'Label', 'Scenario', 'Technique', 'Justification', 'Full Response'])

def get_processed_ids(output_df):
    """Get a list of IDs that have already been processed"""
    if output_df.empty:
        return []
    
    return output_df['ID'].tolist()

# We don't need these functions anymore since we're using IDs for tracking

def process_csv(technique, input_file, output_file, output_file_combined, theory, model):
    # Read input CSV
    input_df = pd.read_csv(input_file, encoding='ISO-8859-1')
    # input_df = input_df[:2000]  # Limit to 500 rows for testing

    # Ensure there's an 'id' column
    if 'id' not in input_df.columns:
        input_df['id'] = range(1, len(input_df) + 1)
    
    # Load existing output DataFrame or create a new one
    output_df = load_output_dataframe(output_file)
    
    # Get list of IDs already processed
    processed_ids = get_processed_ids(output_df)
    print(f"Found {len(processed_ids)} already processed rows")
    
    # Create a list to hold all rows, keeping the input order
    all_rows = []
    
    # First, add placeholder None for each input row to maintain order
    for _ in range(len(input_df)):
        all_rows.append(None)
    
    # Fill in the already processed rows
    for _, row in output_df.iterrows():
        row_id = row['ID']
        # Find the position of this ID in the input DataFrame
        try:
            input_position = input_df[input_df['id'] == row_id].index[0]
            all_rows[input_position] = row.to_dict()
        except (IndexError, KeyError):
            print(f"Warning: Row ID {row_id} in output file not found in input file")
    
    # Now process each row in the input CSV that's still None
    for index, row in input_df.iterrows():
        row_id = row['id']
        
        # Skip if this row is already processed
        if all_rows[index] is not None:
            continue
        
        print(f"Processing missing row {row_id} at index {index}")
        
        # Extract scenario based on theory
        if theory == 'Commonsense':
            label = row['label']
            scenario = row['input']
        elif theory == 'Justice':
            label = row['label']
            scenario = row['scenario']
        elif theory == 'Virtue':
            label = row['label']
            scenario = ["", ""] 
            scenario[0] = row['scenario']
            scenario[1] = row['virtue']
        elif theory == 'Utilitarianism':
            label = row['label']
            scenario = ["", ""] 
            scenario[0] = row['Scenario1']
            scenario[1] = row['Scenario2']
        elif theory == 'Deontology':
            label = row['label']
            scenario = ["", ""] 
            scenario[0] = row['scenario']
            scenario[1] = row['excuse']
        
        # Generate the prompt
        prompt = generate_prompt(technique, scenario, theory)

        # Query the appropriate model
        try:
            if model == "llama2":
                full_response, score, justification = query_ollama2(prompt)
            elif model == "llama3.1":
                full_response, score, justification = query_ollama3(prompt)
            elif model == "gemini":
                full_response, score, justification = query_gemini(prompt)
            elif model == "openai":
                full_response, score, justification = query_openai(prompt)
            elif model == "gpt2":
                full_response, score, justification = query_gpt2(prompt)
            elif model == "mistral":
                full_response, score, justification = query_mistral(prompt)
            elif model == "bert":
                full_response, score, justification = query_bert(prompt)
            elif model == "roberta":
                full_response, score, justification = query_roberta_large(prompt)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            print(f"Error querying model: {e}")
            # Set default values for when model fails
            full_response = "ERROR: Model response failed"
            score = float('nan')  # NaN for numerical values
            justification = "ERROR: Model response failed"

        # Now add the result regardless of whether there was a response or not
        # This ensures rows with errors are still included in the output
        result = {
            'ID': row_id,
            'Label': label,
            'Scenario': scenario,
            technique: score,
            'Justification': justification,
            'Full Response': full_response
        }
        
        # Add to the all_rows list at the correct position
        all_rows[index] = result
        
        # Also prepare combined results if needed
        result_combined = {
            'ID': row_id,
            'Label': label,
            'Scenario': scenario,
            technique: score,
            f'{technique}_Justification': justification,
        }
        
        # Update the output file immediately with all processed rows so far
        # Filter out None values (unprocessed rows)
        processed_rows = [row for row in all_rows if row is not None]
        current_output_df = pd.DataFrame(processed_rows)
        
        # Write to CSV
        if not current_output_df.empty:
            current_output_df.to_csv(output_file, index=False)
            print(f"Updated output file with {len(processed_rows)} rows")
        
        # Adding sleep to avoid rate limiting
        time.sleep(1)
    
    # Final check to make sure all rows were processed
    processed_rows = [row for row in all_rows if row is not None]
    print(f"Total rows processed: {len(processed_rows)} out of {len(input_df)}")
    
    if len(processed_rows) < len(input_df):
        print("Warning: Some rows could not be processed!")
    
    # Convert to final DataFrame
    final_output_df = pd.DataFrame(processed_rows)
    
    # Do a final write to ensure everything is saved
    if not final_output_df.empty:
        final_output_df.to_csv(output_file, index=False)
    
    return processed_rows

# No longer needed as we're writing the entire DataFrame at once

def main():
    theories = ['Commonsense', 'Justice', 'Virtue', 'Utilitarianism', 'Deontology']
    theory = theories[0]  # Default to Commonsense

    # Creating a parser to get the argument from command-line
    parser = argparse.ArgumentParser()

    # Defaulting to Detailed0-shot if not provided explicitly
    # parser.add_argument('--technique', type=str, default='Detailed32-shot_CoT', help='Prompting technique')
    # parser.add_argument('--technique', type=str, default='Detailed2-shot', help='Prompting technique')

    parser.add_argument('--model', type=str, default='gemini', help='Model')
    parser.add_argument('--theory', type=str, default='Commonsense', help='Ethical theory to test')
    parser.add_argument('--input_file', type=str, help='Override the default input file')
    parser.add_argument('--output_file', type=str, help='Override the default output file')
 
    args = parser.parse_args()
    # technique = args.technique
    model = args.model
    theory = args.theory if args.theory in theories else theories[0]

    # Get the current directory
    current_dir = os.getcwd()
    
    # Set input file based on theory or override with argument
    if args.input_file:
        input_file = args.input_file
    else:
        if theory == 'Commonsense':
            # input_file = os.path.join(current_dir, 'Ethics/commonsense/cm_test.csv')
            input_file = os.path.join(current_dir, 'Ethics/commonsense/cm_test_hard.csv')

        elif theory == 'Justice':
            input_file = os.path.join(current_dir, 'Ethics/justice/justice_test.csv')
            # input_file = os.path.join(current_dir, 'Ethics/justice/justice_test_hard.csv')

        elif theory == 'Virtue':
            input_file = os.path.join(current_dir, 'Ethics/virtue/virtue_test_modified.csv')
            # input_file = os.path.join(current_dir, 'Ethics/virtue/virtue_test_hard_modified.csv')

        elif theory == 'Utilitarianism':
            input_file = os.path.join(current_dir, 'Ethics/utilitarianism/util_test.csv')
            # input_file = os.path.join(current_dir, 'Ethics/utilitarianism/util_test_hard.csv')

        elif theory == 'Deontology':
            input_file = os.path.join(current_dir, 'Ethics/deontology/deontology_test.csv')
            # input_file = os.path.join(current_dir, 'Ethics/deontology/deontology_test_hard.csv')

    # for technique in ['Detailed0-shot', 'Detailed0-shot_CoT', 'Detailed1-shot', 'Detailed1-shot_CoT', 'Detailed2-shot', 'Detailed2-shot_CoT', 'Detailed8-shot', 'Detailed32-shot']:
    # for technique in ['Detailed0-shot', 'Detailed1-shot_CoT', 'Detailed2-shot', 'Detailed2-shot_CoT', 'Detailed8-shot', 'Detailed32-shot']: #CS_TH
    for technique in ['Detailed1-shot']:

        if args.output_file:
            output_file = args.output_file
        else:
            type = 'TestHard' # train, test, test_hard
            # type = 'Test'
            output_file = os.path.join(current_dir, f'{model}_{theory}_{technique}_{type}.csv')

        output_file_combined = os.path.join(current_dir, f'{model}_{theory}.csv')

        print(f"Processing theory: {theory}")
        print(f"Using model: {model}")
        print(f"Using technique: {technique}")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        
        # Calling the process_csv function 
        process_csv(technique, input_file, output_file, output_file_combined, theory, model)
        
        print("Processing complete!")

if __name__ == "__main__":
    main()