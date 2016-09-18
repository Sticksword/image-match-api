import requests, json

import base64

with open('IMG_0670.jpg', 'rb') as image_file:
  encoded_string = base64.b64encode(image_file.read())


url = "http://localhost:5000/api/match_image"

headers = {
  'Content-Type': "application/json",
  'cache-control': "no-cache",
}

data = {
  'file': encoded_string,
  'top': 0,
  'left': 0,
  'width': 1000,
  'height':1000
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.text)
