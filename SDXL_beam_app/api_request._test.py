# curl -X POST \
#   --compressed 'https://u7gzo-65e22da152f4bb000761d764.apps.beam.cloud' \
#   -H 'Accept: */*' \
#   -H 'Accept-Encoding: gzip, deflate' \
#   -H 'Authorization: Basic ODdhNWQxYWUzZTdmZTIxMDQ2YWViMTVmN2JmMmMwNDg6NjAxYjEyZDBjZmVlYzc1ZjczMzFjYzFlODdkZWY2ZWE=' \
#   -H 'Connection: keep-alive' \
#   -H 'Content-Type: application/json' \
#   -d '{}'

import requests
import json
import ast
from PIL import Image
from io import BytesIO
import base64

# Convert Base64 to Image
def b64_2_img(data):
    buff = BytesIO(base64.b64decode(data))
    return Image.open(buff)

url = "https://u7gzo-65e2808a52f4bb000761d766.apps.beam.cloud"
payload = {"prompt":"A ginger cat playing",
           "num_inference_steps":20,
           "guidance_scale":7.5}
AUTH_CRED = "ODdhNWQxYWUzZTdmZTIxMDQ2YWViMTVmN2JmMmMwNDg6NjAxYjEyZDBjZmVlYzc1ZjczMzFjYzFlODdkZWY2ZWE="
headers = {
  "Accept": "*/*",
  "Accept-Encoding": "gzip, deflate",
  "Authorization": "Basic " + AUTH_CRED,
  "Connection": "keep-alive",
  "Content-Type": "application/json"
}

response = requests.request("POST", url, 
  headers=headers,
  data=json.dumps(payload)
)

dict_str = response.content.decode('utf-8')
json_data = ast.literal_eval(dict_str)
decoded_bytes = base64.b64decode(json_data["b64_image"])

# First, decode the base64 string back to bytes
# decoded_bytes = base64.b64decode(response.content)

# Then, write the bytes to a new file
with open("recovered_image.jpg", "wb") as recovered_file:
    recovered_file.write(decoded_bytes)

print(response)

# new_img = b64_2_img(img_b64)