from flask import Flask, jsonify, abort, make_response, request
from PIL import Image
import requests
import json
import base64

# from io import BytesIO
from cStringIO import StringIO # fk so many, from cStringIO to StringIO to BytesIO

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

tasks = [
  {
    'id': 1,
    'title': 'Buy groceries',
    'description': 'Milk, Cheese, Pizza, Fruit, Tylenol', 
    'done': False
  },
  {
    'id': 2,
    'title': u'Learn Python',
    'description': u'Need to find a good Python tutorial on the web', 
    'done': False
  }
]

##############################################################
# Routes
##############################################################

@app.route('/todo/tasks', methods=['GET'])
def get_tasks():
  return jsonify({'tasks': tasks})


@app.route('/todo/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
  task = [task for task in tasks if task['id'] == task_id]
  if len(task) == 0:
    abort(404)
  return jsonify({'task': task[0]})


@app.route('/todo/tasks', methods=['POST'])
def create_task():
  if not request.json or not 'title' in request.json:
    abort(400)
  task = {
    'id': tasks[-1]['id'] + 1,
    'title': request.json['title'],
    'description': request.json.get('description', ""),
    'done': False
  }
  tasks.append(task)
  return jsonify({'task': task}), 201


@app.route('/todo/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
  task = [task for task in tasks if task['id'] == task_id]
  if len(task) == 0:
    abort(404)
  if not request.json:
    abort(400)
  if 'title' in request.json and type(request.json['title']) != unicode:
    abort(400)
  if 'description' in request.json and type(request.json['description']) is not unicode:
    abort(400)
  if 'done' in request.json and type(request.json['done']) is not bool:
    abort(400)
  task[0]['title'] = request.json.get('title', task[0]['title'])
  task[0]['description'] = request.json.get('description', task[0]['description'])
  task[0]['done'] = request.json.get('done', task[0]['done'])
  return jsonify({'task': task[0]})


@app.route('/todo/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
  task = [task for task in tasks if task['id'] == task_id]
  if len(task) == 0:
    abort(404)
  tasks.remove(task[0])
  return jsonify({'result': True})


@app.route('/api/match_image', methods=['POST'])
def match_image():
  print 'hello from match_image'
  print request.headers

  if request.headers['Content-Type'] == 'application/json':
    # with open('temp-byte-string.txt', 'wb') as output:
    #   output.write(bytearray(request.data))
    # print type(request.get_data())
    # json.loads(request.get_data())
    # print request.get_json(force=True)
    # print request.json
    box = (request.json['top'], request.json['left'], request.json['left'] + request.json['width'], request.json['top'] + request.json['height'])

    head_crop = get_head_crop_from_byte_string(request.json['file'], box) # (left, top, right bot)
    head_crop_file = StringIO()
    head_crop = head_crop.rotate(-90)
    # head_crop.show() # display the image
    # head_crop.save('lemme-see.jpg') 
    head_crop.save(head_crop_file, format='JPEG') # save PIL image into image file
    detection_result = detect_face(head_crop_file.getvalue()) # pass image file byte value

    if not detection_result:
      print 'no face detected'
      return jsonify({'match': False})
    else:
      # print 'result from face detection:'
      # print type(result)
      # print type(result[0])
      similarity_result = find_similar(detection_result[0]['faceId'], 'hack-the-north-michael')
      if not similarity_result:
        print 'no match found'
        return jsonify({'match': False})
      else:
        return jsonify({'match': True})

  else:
    return jsonify({'error': 'no pls, i only like jason'})

  # file = request.files['file']
  # if file and allowed_file(file.filename):
  #   print '**received file: ', file.filename
  #   print file
  #   return jsonify({'success': 'good job'})
  # else:
  #   return jsonify({'error': 'bad input file type'})


@app.route('/')
def home():
  print 'hello from /'
  return 'The North Remembers'


@app.errorhandler(404)
def not_found(error):
  return make_response(jsonify({'error': 'Not found'}), 404)


##############################################################
# private methods
##############################################################

def get_head_crop_from_byte_string(file_string, box):
  print 'hello from get_head_crop_from_byte_string'

  # print file_string
  # byte_string = file_string.encode('utf-8')
  # print byte_string
  # decoded = file_string.decode('utf-8')
  decoded = base64.b64decode(file_string)
  print decoded
  imgFile = StringIO(decoded)
  img = Image.open(imgFile)

  # with open('private_pic.jpg', 'wb') as file_handle
  #   file_handle.write(byte_string.decode('base64'))
  
  # img = Image.open('private_pic.jpg')

  # box is a tuple: (left, top, right bot)
  return img.crop(box)


def detect_face(byte_string):
  print 'hello from detect_face'
  url = "https://api.projectoxford.ai/face/v1.0/detect"

  headers = {
    'ocp-apim-subscription-key': "46f043d347ce47a8a66b3d734ac18128",
    'Content-Type': "application/octet-stream",
    'cache-control': "no-cache",
  }
  # data = open('IMG_0670.jpg', 'rb').read()

  response = requests.post(url, headers=headers, data=byte_string)
  # print response.text
  return response.json()


def find_similar(faceId, faceListId):
  print 'hello from find_similar'
  url = "https://api.projectoxford.ai/face/v1.0/findsimilars"

  headers = {
    'ocp-apim-subscription-key': "46f043d347ce47a8a66b3d734ac18128",
    'Content-Type': "application/json",
    'cache-control': "no-cache",
  }

  data = {
    'faceId': faceId,
    'faceListId': faceListId
  }

  response = requests.post(url, headers=headers, data=json.dumps(data))
  print response.text
  return response.json()





if __name__ == '__main__':
  app.run(debug=True)
