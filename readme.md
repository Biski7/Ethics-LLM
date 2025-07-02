# TOWARDS ETHICAL AI
* Create a virtualEnv and activate it
> Install the requirements 
conda activate ...

* Different prompts are: 
> "Base0-shot", "Base0-shot_CoT", "Base1-shot", "Base1-shot_CoT", "Base2-shot", "Base2-shot_CoT", "Detailed0-shot", "Detailed0-shot_CoT", "Detailed1-shot", "Detailed1-shot_CoT", "Detailed2-shot", "Detailed2-shot_CoT"

### RUNNING THE CODE
* Running Base0-shot (Run this base shot for experimentation)
* It takes 2 argument. The technique and the model. The files are automatically created and named appropriately.
python inference.py --technique 'Base0-shot' --model 'gpt2'
python inference.py --technique 'Base0-shot' --model 'bert'

* * Running the ollama model
* Install ollama thorugh ollama.com and download the appropriate version
* Start ollama 
* Default port is 11434
* Go to terminal and type the following:
    ollama serve
* Type this in a new terminal:
    ollama pull llama2



* Create a .env file and paste the following
openai_key="..."
genai_key="..."
HUGGINGFACE_API_KEY="..."

> Create accounts at respective domains and generate the api keys and paste it in the .env file

