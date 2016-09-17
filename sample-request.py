import requests

# url = 'http://httpbin.org/post'
# files = {'file': open('sample.txt', 'rb')}

# r = requests.post(url, files=files)
# print r.text


url = "https://api.projectoxford.ai/face/v1.0/detect"

headers = {
  'ocp-apim-subscription-key': "46f043d347ce47a8a66b3d734ac18128",
  'Content-Type': "application/octet-stream",
  'cache-control': "no-cache",
}

data = open('IMG_0670.jpg', 'rb').read()

response = requests.post(url, headers=headers, data=data)

print(response.text)
