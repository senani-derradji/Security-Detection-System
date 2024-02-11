from flask import Flask, render_template, Response, request, redirect, url_for
import cv2, face_recognition , os

app = Flask(__name__, static_url_path='/static')

# Define the correct username and password
CORRECT_USERNAME = "derradji"
CORRECT_PASSWORD = "derradji"

paths = ["static/images/" + file for file in os.listdir("static/images") if file.endswith(".jpg")]
known_face_encodings = [face_recognition.face_encodings(face_recognition.load_image_file(path))[0] for path in paths]
known_face_names = [os.path.splitext(os.path.basename(path))[0] for path in paths]
cap = cv2.VideoCapture(0)

# Set a smaller frame size for processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Number of frames to skip before processing
SKIP_FRAMES = 5
frame_count = 0

def detect_faces():
    global frame_count
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % SKIP_FRAMES != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            detected_name = known_face_names[matches.index(True)] if True in matches else "Unknown"
            color = (0, 255, 0) if detected_name != "Unknown" else (0, 0, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, detected_name, (left, top - 15), cv2.FONT_ITALIC, 0.75,
                        (0, 255, 0) if detected_name != "Unknown" else (0, 0, 255), 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# @app.route('/')
# def index():
#     return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == CORRECT_USERNAME and password == CORRECT_PASSWORD:
            return render_template('index.html')
        else:
            return "Sorry, you can't open this page. Invalid username or password."
    return render_template('login.html')

@app.route('/video_feed')
def video_feed():
    return Response(detect_faces(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
