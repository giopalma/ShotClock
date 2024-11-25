from typing import List
import cv2 as cv
import numpy as np
import time
from preset import Preset
from utils.ball import Ball, check_ball_movement, detect_balls, draw_balls
from utils.colors import hex_to_opencv_hsv
from utils.mask import create_mask


def main():
    vc = cv.VideoCapture("./test_data/video/example.mp4")
    # TODO: Questo lavoro di preset e cambio colore HEX -> HSV deve essere fatto durante la fase di setup quando viene creato il preset
    colors = ["#45c6ed", "#2288b5", "#1978a2", "#3bbbf3", "#0b6d9e"]
    preset = Preset(
        id=0,
        name="Example",
        points=[(120, 80), (520, 80), (520, 280), (120, 280)],
        table_colors=[hex_to_opencv_hsv(color) for color in colors],
    )
    table_colors = preset.table_colors

    points = np.array(preset.points, dtype=np.int32)

    previous_balls: List[Ball] = []
    frame_count = 0
    i = 0
    is_ball_moving_arr = np.zeros(3)
    while vc.isOpened():
        start_time = time.time()
        frame_count = frame_count + 1

        ret, frame = vc.read()

        if not ret:
            vc.set(cv.CAP_PROP_POS_FRAMES, 0)
            continue

        blurred = cv.GaussianBlur(frame, (5, 5), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        mask = create_mask(hsv, points, table_colors)

        current_balls = detect_balls(mask, frame_count)
        if frame_count % 10 == 0:
            is_ball_moving_arr[i % 3] = check_ball_movement(
                previous_balls, current_balls
            )
            i = i + 1
            # is_ball_moving = check_ball_movement(previous_balls, current_balls)
            previous_balls = current_balls
        draw_balls(previous_balls, frame)
        for ball in current_balls:
            cv.circle(frame, ball.position, 30, color=(0, 255, 0), thickness=1)

        # === TEXT ===

        if np.all(is_ball_moving_arr == 0):
            cv.putText(
                frame,
                "Ball not moving",
                (10, 60),
                cv.FONT_HERSHEY_SIMPLEX,
                0.7,
                (21, 20, 123),
                2,
                cv.LINE_AA,
            )
        else:
            cv.putText(
                frame,
                "Ball moving",
                (10, 60),
                cv.FONT_HERSHEY_SIMPLEX,
                0.7,
                (21, 20, 123),
                2,
                cv.LINE_AA,
            )

        cv.putText(
            frame,
            "ESC per uscire",
            (10, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (21, 20, 123),
            2,
            cv.LINE_AA,
        )

        cv.imshow("Video", frame)

        elapsed_time = time.time() - start_time
        FRAMERATE = 30
        time.sleep(max(0, 1 / FRAMERATE - elapsed_time))

        if cv.waitKey(1) & 0xFF == 27:  # Exit with ESC key
            break

    vc.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
