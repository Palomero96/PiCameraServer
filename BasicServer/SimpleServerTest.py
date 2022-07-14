from flask import Flask, render_template, Response
import cv2

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

app = Flask(__name__)

def getFrames():
    while True:
        ret, img = cam.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                    frame + b'\r\n')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/streaming")
def streaming():
    return Response(getFrames(), mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    app.run()


cam.release()