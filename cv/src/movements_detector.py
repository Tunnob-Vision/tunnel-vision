import cv2
import mediapipe as mp
from collections import deque
import math
import numpy as np

# -------------------------
# Parameters
# -------------------------
VIDEO_PATH = "input.mp4"
OUTPUT_PATH = "annotated_output.mp4"
HISTORY_LENGTH = 10       # frames to compute motion
MIN_MOVEMENT = 0.02       # normalized movement threshold
FINGER_OPEN_THRESHOLD = 0.8  # ratio to decide if fingers are open

# -------------------------
# MediaPipe setup
# -------------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# -------------------------
# Helper functions
# -------------------------
def distance(a, b):
    """Euclidean distance between two points"""
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

def finger_open_ratio(hand_landmarks):
    """
    Compute a simple "finger openness" ratio:
    - average distance fingertip → palm center normalized by hand size
    """
    wrist = hand_landmarks.landmark[0]
    middle_finger_tip = hand_landmarks.landmark[12]
    hand_size = distance(wrist, middle_finger_tip)

    tips = [hand_landmarks.landmark[i] for i in [8, 12, 16, 20]]  # index, middle, ring, pinky
    ratios = [distance(wrist, tip)/hand_size for tip in tips]
    return sum(ratios)/len(ratios)

def motion_vector(history):
    """
    Compute motion vector between first and last frames in history
    """
    if len(history) < 2:
        return 0, 0
    x0, y0, _ = history[0]
    x1, y1, _ = history[-1]
    return x1 - x0, y1 - y0

# -------------------------
# Video setup
# -------------------------
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(OUTPUT_PATH, fourcc, fps, (width, height))

# Hand history for motion tracking
hand_histories = {}

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb)

    # Track each hand
    if results.multi_hand_landmarks:
        for idx, hl in enumerate(results.multi_hand_landmarks):
            # Store wrist position history
            wrist = hl.landmark[0]
            if idx not in hand_histories:
                hand_histories[idx] = deque(maxlen=HISTORY_LENGTH)
            hand_histories[idx].append((wrist.x, wrist.y, wrist.z))

            # Compute motion
            dx, dy = motion_vector(hand_histories[idx])

            # Finger openness
            openness = finger_open_ratio(hl)

            # -------------------------
            # Rules-based gesture detection
            # -------------------------
            gesture = None
            # CHECK: hand taps downward, fingers open
            if dy > MIN_MOVEMENT and openness > FINGER_OPEN_THRESHOLD:
                gesture = "CHECK"
            # FOLD: hand moves forward (toward table), fingers partially closed
            elif dy > MIN_MOVEMENT and openness < FINGER_OPEN_THRESHOLD:
                gesture = "FOLD"
            # RAISE: hand moves upward, fingers open
            elif dy < -MIN_MOVEMENT and openness > FINGER_OPEN_THRESHOLD:
                gesture = "RAISE"

            # Draw hand and gesture label
            mp_drawing.draw_landmarks(
                frame, hl, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            if gesture:
                cx = int(wrist.x * width)
                cy = int(wrist.y * height)
                cv2.putText(frame, gesture, (cx - 30, cy - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Write annotated frame
    out.write(frame)
    frame_idx += 1
    if frame_idx % 50 == 0:
        print(f"Processed frame {frame_idx}")

cap.release()
out.release()
print("Done! Annotated video saved as", OUTPUT_PATH)
