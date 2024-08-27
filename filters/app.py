from flask import Flask, Response, request, jsonify
import cv2
import numpy as np
import mediapipe as mp
import time

app = Flask(__name__)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Initialize Mediapipe hand model
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Define filters
def apply_filter(frame, filter_type):
    if filter_type == 'gray':
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif filter_type == 'sepia':
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        return cv2.transform(frame, kernel)
    elif filter_type == 'negative':
        return cv2.bitwise_not(frame)
    elif filter_type == 'blur':
        return cv2.GaussianBlur(frame, (15, 15), 0)
    else:
        return frame

filters = ['original', 'gray', 'sepia', 'negative', 'blur']
current_filter_index = 0
start_pos = None
swipe_threshold = 50
last_swipe_time = time.time()

@app.route('/video_feed')
def video_feed():
    def generate():
        global start_pos, current_filter_index, last_swipe_time

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    index_finger_pos = (int(index_finger_tip.x * 640), int(index_finger_tip.y * 480))

                    if start_pos is None:
                        start_pos = index_finger_pos
                    else:
                        diff_x = index_finger_pos[0] - start_pos[0]
                        if abs(diff_x) > swipe_threshold and (time.time() - last_swipe_time) > 1:
                            if diff_x > 0:  # Swipe right
                                current_filter_index = (current_filter_index + 1) % len(filters)
                            last_swipe_time = time.time()
                            start_pos = index_finger_pos

            if filters[current_filter_index] == 'original':
                filtered_frame = frame.copy()
            else:
                filtered_frame = apply_filter(frame.copy(), filters[current_filter_index])

            _, buffer = cv2.imencode('.jpg', filtered_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_filter', methods=['GET'])
def get_current_filter():
    return jsonify({'filter': filters[current_filter_index]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
