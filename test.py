import cv2 as cv
import numpy as np
import imutils
import time
from preset import Preset
from utils import hex_to_opencv_hsv


def create_mask(hsv, points, table_colors):
    h_diff, s_diff, v_diff = 5, 10, 5
    color_lower = tuple(
        min(color[i] for color in table_colors) - diff
        for i, diff in enumerate([h_diff, s_diff, v_diff])
    )
    color_upper = tuple(
        max(color[i] for color in table_colors) + diff
        for i, diff in enumerate([h_diff, s_diff, v_diff])
    )

    rec_mask = cv.fillPoly(np.zeros(hsv.shape[:2], dtype=np.uint8), [points], 255)
    color_mask = cv.bitwise_not(cv.inRange(hsv, color_lower, color_upper))
    color_mask = cv.erode(color_mask, None, iterations=3)
    color_mask = cv.dilate(color_mask, None, iterations=2)

    return cv.bitwise_and(color_mask, rec_mask)


def detect_balls(mask):
    cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    centers = []

    for c in cnts:
        area = cv.contourArea(c)
        perimeter = cv.arcLength(c, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter)

        if circularity > 0.8:
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (
                (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if M["m00"] != 0
                else None
            )
            centers.append((center, int(x), int(y), int(radius)))

    return centers


def main():
    vc = cv.VideoCapture("./data/video/example.mp4")
    preset = Preset(
        [(120, 80), (520, 80), (520, 280), (120, 280)],
        ["#45c6ed", "#2288b5", "#1978a2", "#3bbbf3", "#0b6d9e"],
    )
    table_colors = [hex_to_opencv_hsv(color) for color in preset.colors]
    points = np.array(preset.points, dtype=np.int32)

    FRAMERATE = 30

    while vc.isOpened():
        ret, frame = vc.read()
        start_time = time.time()

        if not ret:
            vc.set(cv.CAP_PROP_POS_FRAMES, 0)
            continue

        blurred = cv.GaussianBlur(frame, (5, 5), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        mask = create_mask(hsv, points, table_colors)
        centers = detect_balls(mask)

        for center, x, y, radius in centers:
            cv.circle(frame, (x, y), radius, (0, 255, 255), 2)
            if center:
                cv.circle(frame, center, 1, (0, 0, 255), -1)

        cv.imshow("Video", frame)

        elapsed_time = time.time() - start_time
        time.sleep(max(0, 1 / FRAMERATE - elapsed_time))

        if cv.waitKey(1) & 0xFF == 27:  # Exit with ESC key
            break

    vc.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
