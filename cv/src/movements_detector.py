import cv2
import time
import argparse
import os
import mediapipe as mp
from collections import defaultdict, deque

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


# -------------------------
# Argument parsing
# -------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Webcam hand tracker (MediaPipe)")
    p.add_argument("--camera", "-c", type=int, default=0)
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=720)
    p.add_argument("--save-dir", type=str, default="captures")
    return p.parse_args()


# -------------------------
# Hand Tracking Manager
# -------------------------
class HandTracker:
    def __init__(self, history_length=15):
        self.history = defaultdict(lambda: deque(maxlen=history_length))
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.table_level = None

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb)

    def update_history(self, results):
        """
        Store wrist positions (landmark 0) for motion-based detection
        """
        if not results.multi_hand_landmarks:
            return

        for idx, hl in enumerate(results.multi_hand_landmarks):
            wrist = hl.landmark[0]
            self.history[idx].append((wrist.x, wrist.y, wrist.z))

    def draw(self, frame, results):
        if not results.multi_hand_landmarks:
            return

        for hl in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hl,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

    def detect_check(self, hand_id, threshold=0.02, min_tap_speed=0.02):
        hist = list(self.history[hand_id])
        if len(hist) < 5:
            return False

        # Extract y movement (vertical direction)
        ys = [p[1] for p in hist]  # (x, y, z)
        dy = ys[-1] - ys[-5]  # movement over last ~5 frames

        # Must move downward fast
        if dy > min_tap_speed:
            # close to table
            if self.table_level is not None and ys[-1] > (self.table_level - threshold):
                return True

        return False



# -------------------------
# Main Loop
# -------------------------
def main():
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    cap = cv2.VideoCapture(args.camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    tracker = HandTracker()

    print("Press 's' to save, 'q' to quit.")

    prev_time = time.time()
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("ERROR: No frame")
            break

        # FPS
        frame_count += 1
        elapsed = time.time() - prev_time
        fps = frame_count / elapsed

        # Detect hands
        results = tracker.process(frame)
        tracker.update_history(results)
        for hand_id in tracker.history.keys():
            if tracker.detect_check(hand_id):
                print("CHECK detected for hand", hand_id)
                cv2.putText(frame, "CHECK!", (200, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 3)

        tracker.draw(frame, results)

        # Debug print (optional)
        # print(tracker.history)

        # UI overlays
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        cv2.imshow("Webcam", frame)

        # Key controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        if key == ord('t'):
            for hand_id, h in tracker.history.items():
                tracker.table_level = sum(p[1] for p in h) / len(h)
                print("Table calibrated at", tracker.table_level)


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
