# Import necessary libraries
from flask import Flask, render_template, Response, request
import cv2
import datetime, time
import os
from threading import Thread
from story import story_gen

# Define global variables
global capture, rec_frame, switch, out, last_frame
capture = 0
# switch = 1
rec_frame = None
out = None
last_frame = None

# Create a directory for saving captured images
try:
    os.mkdir('./shots')
except OSError as error:
    pass

# Load pretrained face detection model
# net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')

# Instantiate Flask app
app = Flask(__name__, template_folder='./templates')

# Open the default camera (camera index 0)
camera = cv2.VideoCapture(0)

# Function to generate frames from the camera
def gen_frames():
    global out, capture, rec_frame, last_frame
    i = 1
    while True and i < 7:
        success, frame = camera.read()
        if success:
            # Apply image processing options based on global variables
            if capture:
                capture = 0
                p = os.path.sep.join(['static/images', f"story{i}.png"])
                cv2.imwrite(p, frame)
                i+=1
                
            # if switch == 1:
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                last_frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
                # cv2.imshow("photo", frame)
            except Exception as e:
                #print(e)
                pass
        
            # if last_frame is not None:
            #     yield (b'--frame\r\n'
            #            b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
        else:
            # print("did not pass")
            pass

# Flask route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route for streaming video feed
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Flask route for handling form submissions
@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global switch, camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture = 1
        # elif request.form.get('start') == 'Start':
        #     global switch
        #     switch = not switch
        #     if switch:
        #         camera = cv2.VideoCapture(0)
    elif request.method == 'GET':
        return render_template('index.html')
    return render_template('index.html')

@app.route('/story', methods=['POST'])
def story_generate():
    story = story_gen()
    return render_template('index.html', story_index = story)



# Run the Flask app
if __name__ == '__main__':
    app.run()

# Release the camera and close all OpenCV windows when the program ends
camera.release()
cv2.destroyAllWindows()
























