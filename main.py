import json
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", api_key="api_key")

sys_prompt = """
You are a helpful assistant who helps user in making finetuning datasets based on the context provided.
You never hallucinate new information you never miss the format while answering.
The questions and answer you produce should be of the highest quality and should allow any llm to grasp the context when finetuned on it.
Format is json with two variables question and answer. 
You can make as many questions as you want and you have to make as many questions as possible to but they should be relevant to the context provided.
REMEMBER to always answer in json format and we dont need any pretext, context, concusion or any acknowledgement of the context or response you generate.
Always make sure include all the examples which are in the context in questions and answers.
Here is an example response i expect from you:
```json
[
  {
    "question": "A question from the context",
    "answer": "Answer from the context"
  },
  ...
]
```
Always answer in the defined format and never miss the format.REMEMBER if you miss the format something bad will happen.
"""

def extract_json_from_response(response):
    start_marker = "```json"
    end_marker = "```"
    start_index = response.find(start_marker)
    end_index = response.find(end_marker, start_index + len(start_marker))

    if start_index != -1 and end_index != -1:
        json_str = response[start_index + len(start_marker):end_index].strip()
    else:
        json_str = ""
        print("JSON part not found in the response.")

    return json_str

def process_context(context, retries=3):
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Extract questions and answers following our format from {context}"}
    ]

    for attempt in range(retries):
        response = llm.invoke(messages).content
        print(f"Attempt {attempt + 1}: {response}")

        json_str = extract_json_from_response(response)

        try:
            json_response = json.loads(json_str)
            return json_response
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON on attempt {attempt + 1}: {e}")
            if attempt == retries - 1:
                return []


input_file = 'filtered_docs.txt'
output_file = 'qa.json'


with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

contexts = content.strip().split('==================================================')


try:
    with open(output_file, 'r') as f:
        all_qa = json.load(f)
except FileNotFoundError:
    all_qa = []


for context in contexts:
    if context.strip():
        qa_data = process_context(context.strip())
        all_qa.extend(qa_data)


with open(output_file, 'w') as f:
    json.dump(all_qa, f, indent=4)

print(f"JSON data has been saved to {output_file}")