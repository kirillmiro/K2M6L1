import json
import time
import base64
import requests


class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt  # исправлено, чтобы вставлялся реальный prompt
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)
        raise Exception("Generation not completed in time.")


def generate_image_from_text(prompt, API_url, API_key, SECRET_key):
    api = FusionBrainAPI(API_url, API_key, SECRET_key)
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt, pipeline_id)
    files = api.check_generation(uuid)

    saved_files = []
    for i, b64_data in enumerate(files):
        # исправляем паддинг
        b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
        img_bytes = base64.b64decode(b64_data)
        filename = f"image_{i}.png"  # автоматическое уникальное имя
        with open(filename, "wb") as f:
            f.write(img_bytes)
        print(f"Saved {filename}")
        saved_files.append(filename)

    return saved_files


if __name__ == '__main__':
    API_url = 'https://api-key.fusionbrain.ai/'
    API_key = 'DE6767F15635759248E4A6BFFF085F50'
    SECRET_key = '2349A0B69A7355452CEEFBB3DFCEA100'
    prompt = "Cat"
    saved_files = generate_image_from_text(prompt, API_url, API_key, SECRET_key)
    print("All images saved:", saved_files)
