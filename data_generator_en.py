import boto3
import json
import re
from botocore.exceptions import ClientError

# --- 1. Configuration ---
# AWS client setup
client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "meta.llama3-70b-instruct-v1:0"

# Your parameters
category = "toys"
num = 10

# Output file path
output_file_path = f"Datasets/llm-rank-optimizer/extend_data/{category}.jsonl"


# --- 2. Define Prompt (fixed curly brace issue) ---
prompt = f'''
--- Book ---
###
{{"Name": "The Great Adventure", "Author": "John Smith", "Description": "An epic tale of adventure and discovery in uncharted lands.", "Price": "$14.99", "Rating": 4.5, "Genre": "Adventure", "Ideal For": "Adventure lovers"}}
{{"Name": "Mystery of the Lost Key", "Author": "Emily Johnson", "Description": "A gripping mystery novel filled with twists and turns.", "Price": "$12.99", "Rating": 4.2, "Genre": "Mystery", "Ideal For": "Mystery enthusiasts"}}
{{"Name": "The Hidden Treasure", "Author": "Lisa Brown", "Description": "A thrilling adventure of a young explorer searching for hidden treasure.", "Price": "$16.99", "Rating": 4.6, "Genre": "Adventure", "Ideal For": "Treasure hunt enthusiasts"}}
{{"Name": "Whispers in the Dark", "Author": "James White", "Description": "A mystery novel that unravels the secrets of a haunted mansion.", "Price": "$13.99", "Rating": 4.3, "Genre": "Mystery", "Ideal For": "Fans of ghost stories"}}
{{"Name": "Galactic Journey", "Author": "Mark Davis", "Description": "A thrilling science fiction novel exploring the depths of space.", "Price": "$18.99", "Rating": 4.6, "Genre": "Science Fiction", "Ideal For": "Sci-fi fans"}}
{{"Name": "Time Travelers", "Author": "Alice Grey", "Description": "A gripping science fiction story about traveling through time.", "Price": "$15.99", "Rating": 4.4, "Genre": "Science Fiction", "Ideal For": "Time travel enthusiasts"}}
{{"Name": "The Enchanted Island", "Author": "Robert Green", "Description": "An adventure story set on a mysterious island with magical creatures.", "Price": "$17.99", "Rating": 4.7, "Genre": "Adventure", "Ideal For": "Fantasy and adventure lovers"}}
{{"Name": "The Detective's Secret", "Author": "Rachel Black", "Description": "A mystery novel following a detective unraveling a complex case.", "Price": "$14.99", "Rating": 4.5, "Genre": "Mystery", "Ideal For": "Fans of detective stories"}}
{{"Name": "Alien Invasion", "Author": "Michael Star", "Description": "A science fiction novel about defending Earth from an alien invasion.", "Price": "$19.99", "Rating": 4.5, "Genre": "Science Fiction", "Ideal For": "Alien and space battle enthusiasts"}}
{{"Name": "The Lost Expedition", "Author": "Emily Sands", "Description": "An adventurous tale of a team searching for a lost civilization.", "Price": "$16.99", "Rating": 4.8, "Genre": "Adventure", "Ideal For": "Exploration and archaeology fans"}}
###
Based on the format of the examples provided, create a dataset for the product category '{category}'.

Each entry in the dataset must be in valid JSON format and contain the fields: "Description" and "Name".

Generate exactly {num} entries.

Label the category of each product by including the field "Category" with the value '{category}'.

Output the entire dataset in JSONL (JSON Lines) format, where each line is a separate JSON object.

Place the generated JSONL content **only** between the following markers and output nothing else:

### ###
'''

# --- 3. Call Bedrock model ---
# Embed the prompt in Llama 3's instruction format.
formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>user<|end_header_id|>
{prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

# Format the request payload.
native_request = {
    "prompt": formatted_prompt,
    "max_gen_len": 1024,  # Increase maximum generation length appropriately to ensure complete JSONL
    "temperature": 0.7,
}

try:
    # Invoke the model.
    response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
    model_response = json.loads(response["body"].read())
    response_text = model_response["generation"]
    print("--- Raw Model Output ---")
    print(response_text)
    print("------------------------")

except (ClientError, Exception) as e:
    print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
    exit(1)


# --- 4. Parse and save model output to JSONL file ---
def save_jsonl_from_response(text, output_path):
    """
    Extract content between ### and ### from model response using regular expressions,
    and save it as a JSONL file.
    """
    # Regular expression pattern to match content between ###...###
    pattern = r'###(.*?)###'
    match = re.search(pattern, text, re.DOTALL)  # re.DOTALL allows . to match newlines

    if match:
        jsonl_content = match.group(1).strip()
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(jsonl_content)
            print(f"\n✅ Successfully extracted and saved JSONL content to: {output_path}")
        except IOError as e:
            print(f"❌ Error saving file: {e}")
    else:
        print("\n❌ Error: Could not find ### markers or content between them in model response.")
        print("Please check if the model output format matches expectations.")

# Call the function to save model output to file
save_jsonl_from_response(response_text, output_file_path)
