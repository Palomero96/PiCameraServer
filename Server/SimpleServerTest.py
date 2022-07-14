from flask import Flask, render_template, Response, request
import cv2
import os, sys 
import datetime, time
from threading import Thread

global capture, rec, rec_frame, out
capture=0
rec=0

try:
    os.mkdir('./Server/img')
except OSError as error:
    pass

try:
    os.mkdir('./Server/vid')
except OSError as error:
    pass

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)


app = Flask(__name__)

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

def getFrames():
    global capture, rec, rec_frame
    while True:
        ok, img = cam.read()
        if not ok:
            break
        else:
            ok, buffer = cv2.imencode('.jpg', img)
            if(capture):
                capture=0
                now = datetime.datetime.now()
                p = os.path.sep.join(['Server/img', "shot_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, img)

            if(rec):
                rec_frame=img
                img= cv2.putText(cv2.flip(img,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                img=cv2.flip(img,1)

            frame = buffer.tobytes()
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                    frame + b'\r\n')
#https://towardsdatascience.com/camera-app-with-flask-and-opencv-bd147f6c0eec
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global rec
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        elif request.form.get('click') == 'Start Recording':
            rec=1
            if rec:
                rec=1
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('Server/vid/vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                print("Start Recording")
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()


        elif request.form.get('click') == 'Stop Recording':
            rec=0
            if not rec:
                rec=0
                print("Stop Recording")
    elif request.method=='GET':
        return render_template('index.html')
    return render_template('index.html')


@app.route("/streaming")
def streaming():
    return Response(getFrames(), mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run()


cam.release()