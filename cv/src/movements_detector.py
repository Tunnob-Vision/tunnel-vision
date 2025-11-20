import cv2
import time
import argparse
import os
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def parse_args():
    p = argparse.ArgumentParser(description="Simple webcam capture (OpenCV)")
    p.add_argument("--camera", "-c", type=int, default=0, help="Camera index (default 0)")
    p.add_argument("--width", type=int, default=1280, help="Requested capture width")
    p.add_argument("--height", type=int, default=720, help="Requested capture height")
    p.add_argument("--save-dir", type=str, default="captures", help="Directory to save snapshots")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"ERROR: Cannot open camera {args.camera}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    prev_time = time.time()
    frame_count = 0

    print("Press 's' to save a snapshot, 'q' or ESC to quit.")

    # Initialize MediaPipe Hands
    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as hands:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("WARNING: Empty frame received — stopping")
                break

            frame_count += 1
            now = time.time()
            elapsed = now - prev_time
            fps = frame_count / elapsed if elapsed > 0 else 0.0

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Draw landmarks and print coordinates
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    coords = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                    print(coords)
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )

            # Overlay FPS
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(frame, "Press 's' to save, 'q' or ESC to quit", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            cv2.imshow("Webcam", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                ts = time.strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(args.save_dir, f"snapshot_{ts}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Saved snapshot: {filename}")
            elif key == ord('q') or key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
