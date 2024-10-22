from typing import List, Union, Generator, Iterator, Optional
from pprint import pprint
import requests, json, warnings

# Uncomment to disable SSL verification warnings if needed.
# warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class Pipeline:
    def __init__(self):
        self.name = "Dify Agent Pipeline"
        self.api_url = "http://dify.hostname/v1/workflows/run"     # Set correct hostname
        self.api_key = "app-dify-key"                              # Insert your actual API key here.v 
        self.api_request_stream = True                             # Dify support stream
        self.verify_ssl = True
        self.debug = False
    
    async def on_startup(self):
        # This function is called when the server is started.
        print(f"on_startup: {__name__}")
        pass
    
    async def on_shutdown(self): 
        # This function is called when the server is shutdown.
        print(f"on_shutdown: {__name__}")
        pass

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called before the OpenAI API request is made. You can modify the form data before it is sent to the OpenAI API.
        print(f"inlet: {__name__}")
        if self.debug:
            print(f"inlet: {__name__} - body:")
            pprint(body)
            print(f"inlet: {__name__} - user:")
            pprint(user)
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called after the OpenAI API response is completed. You can modify the messages after they are received from the OpenAI API.
        print(f"outlet: {__name__}")
        if self.debug:
            print(f"outlet: {__name__} - body:")
            pprint(body)
            print(f"outlet: {__name__} - user:")
            pprint(user)
        return body

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe: {__name__}")
        
        if self.debug:
            print(f"pipe: {__name__} - received message from user: {user_message}")

        # Set reponse mode Dify API parameter
        if self.api_request_stream is True:
            response_mode = "streaming"
        else:
            response_mode = "blocking"

        # This function triggers the workflow using the specified API.
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            "inputs": {"prompt": user_message},
            "response_mode": response_mode,
            "user": body["user"]["email"]
        }

        response = requests.post(self.api_url, headers=headers, json=data, stream=self.api_request_stream, verify=self.verify_ssl)
        if response.status_code == 200:
            # Process and yield each chunk from the response
            for line in response.iter_lines():
                if line:
                    try:
                        # Remove 'data: ' prefix and parse JSON
                        json_data = json.loads(line.decode('utf-8').replace('data: ', ''))
                        # Extract and yield only the 'text' field from the nested 'data' object
                        if 'data' in json_data and 'text' in json_data['data']:
                            yield json_data['data']['text']
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON: {line}")
        else:
            yield f"Workflow request failed with status code: {response.status_code}"