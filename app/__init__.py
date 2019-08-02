import configparser
import os, logging
import cv2
import numpy as np
from werkzeug import secure_filename
from time import sleep
from flask import Flask, jsonify, request, render_template, send_from_directory, Response
from PIL import Image
from app.camera import VideoCamera

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/dataset/'.format(PROJECT_HOME)
DATASET_FOLDER = 'app/dataset'
TRAINER_YML = 'app/trainer/trainer.yml'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Camera
video_camera = None
global_frame = None

# Training data
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("app/haarcascade_frontalface_default.xml")

def create_new_folder(local_dir):
    newpath = local_dir
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

@app.route('/', methods=['GET','POST','UPDATE','PUT'])
def index():
    response = {}
    return jsonify(response), 200

@app.route('/stream')
def stream():
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate_yml_trainer():
    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(DATASET_FOLDER)
    labels=[0]*len(faces)
    print(ids)
    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write(TRAINER_YML) # recognizer.save() worked on Mac, but not on Pi

    response = {'message': 'success generate ' + TRAINER_YML}
    return jsonify(response), 200

@app.route('/upload', methods = ['POST'])
def upload():
    if request.method == 'POST' and request.files['image']:
        nrp = request.form['nrp']
        img = request.files['image']
        # img_name = secure_filename(img.filename)
        img_name = str(nrp) + "." +  img.filename.split(".")[-1]
        
        create_new_folder(app.config['UPLOAD_FOLDER'])
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)

        file_path, file_extension = os.path.splitext(saved_path)
        
        i = 1
        while os.path.exists(saved_path):
            img_name = nrp + "-" + str(i) + file_extension
            saved_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            i = i + 1

        app.logger.info("saving {}".format(saved_path))
        img.save(saved_path)
        
    return jsonify({'status': 'success', 'data': app.config['UPLOAD_FOLDER'] + img_name}), 200

@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera 
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        return jsonify(result="stopped")

def video_stream():
    global video_camera 
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()
        
    while True:
        frame = video_camera.get_frame()

        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
        yield frame
        yield b'\r\n\r\n'
        

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# function to get the images and label data
def getImagesAndLabels(path):
    width_d, height_d = 280, 280  # Declare your own width and height
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]  

    faceSamples=[]
    ids = []
    for imagePath in imagePaths:
        if imagePath != DATASET_FOLDER + '/.DS_Store':
            print('path = ' + imagePath)
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')
            filename = imagePath.split('/')[-1]
            filename = filename.split('.')[0].split('-')[0]
            faces = detector.detectMultiScale(img_numpy)
            for (x,y,w,h) in faces:
                faceSamples.append(cv2.resize(img_numpy[y:y+h,x:x+w], (width_d, height_d)))
                ids.append(int(filename))
    return faceSamples,ids

