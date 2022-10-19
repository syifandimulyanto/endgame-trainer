import cv2
import threading
import time

class RecordingThread (threading.Thread):
    def __init__(self, name, camera):
        threading.Thread.__init__(self)
        
        self.name = name
        self.isRunning = True
        self.cap = camera

        # face detector
        self.faceDetector = cv2.CascadeClassifier('app/haarcascade_frontalface_default.xml')
        self.gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.out = cv2.VideoWriter('static/video.avi',fourcc, 20.0, (640,480))

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)

        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self):
        # Open a camera
        self.cap = cv2.VideoCapture(0)
      
        # Initialize video recording environment
        self.is_record = False
        self.out = None

        # Thread for recording
        self.recordingThread = None
    
    def __del__(self):
        self.cap.release()
    
    def get_frame(self):
        ret, frame = self.cap.read()

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)

            # Record video
            # if self.is_record:
            #     if self.out == None:
            #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))
                
            #     ret, frame = self.cap.read()
            #     if ret:
            #         self.out.write(frame)
            # else:
            #     if self.out != None:
            #         self.out.release()
            #         self.out = None  

            return jpeg.tobytes()
      
        else:
            return None

    def start_record(self, face_id):
        self.is_record = True
        # self.recordingThread = RecordingThread("Video Recording Thread", self.cap)
        # self.recordingThread.start()
        print('masuk mengambil gambar NRP ' + face_id)
        while(self.is_record):
            ret, img = self.cap.read()
            # img = cv2.flip(img, -1) # flip video image vertically
            face_detector = cv2.CascadeClassifier('app/haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            # face_id = 899812
            count = 0
            t = time.time()
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                count += 1
                # Save the captured image into the datasets folder
                cv2.imwrite("app/dataset/" + str(face_id) + '-' + str(count + int(t * 1000)) + ".jpg", gray[y:y+h,x:x+w])

            if count >= 5:
                self.is_record = False
                # self.recordingThread.stop()
                if self.recordingThread != None:
                    self.recordingThread.stop()
                print('selesai mengambil gambari')
                # break

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()
