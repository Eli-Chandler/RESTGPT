from openai import OpenAI
from flask import Flask

from flask import Flask, request
import json
import re

app = Flask(__name__)

client = OpenAI()


with open('prompt.md') as file:
    pre_prompt = file.read().strip()


def get_gpt_api_response(request_method, request_path, request_args, request_cookies, request_body):
    data = {
        "method": request_method,
        "path": request_path,
        "query": request_args,
        "cookies": request_cookies,
        "body": request_body
    }

    data_string = json.dumps(data, indent=4)
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": pre_prompt},
            {"role": "user", "content": data_string}
        ]
    )

    return parse_api_response(completion.choices[0].message.content)


def parse_api_response(response_text):
    # Use regex to extract the JSON content between the markers
    json_pattern = r'\$\$\$ BEGIN JSON \$\$\$(.*?)\$\$\$ END JSON \$\$\$'
    match = re.search(json_pattern, response_text, re.DOTALL)

    if match:
        json_content = match.group(1).strip()

        # Remove the ```json and ``` markers if present
        json_content = re.sub(r'^```json\s*|\s*```$', '', json_content)

        try:
            # Parse the JSON content
            parsed_response = json.loads(json_content)
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No JSON content found between markers")
        return None




completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
  ]
)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def catch_all(path):
    request_method = request.method
    request_path = "/" + request.path
    request_query = dict(request.args)
    request_cookies = dict(request.cookies)

    request_body = None
    if request.data:
        try:
            request_body = json.loads(request.data)
        except json.JSONDecodeError:
            pass

    completion = get_gpt_api_response(request_method, request_path, request_query, request_cookies, request_body)
    content_type = completion.get('content_type', 'application/json')
    status_code = completion.get('status_code', 200)

    return completion, status_code, {'Content-Type': content_type}





if __name__ == '__main__':
    app.run(debug=True)



print(completion.choices[0].message)