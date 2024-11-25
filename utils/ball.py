import cv2 as cv
from dataclasses import dataclass
from typing import Dict, List, Tuple
from scipy.spatial.distance import euclidean

import imutils
import numpy as np


@dataclass
class Ball:
    position: Tuple[int, int]
    radius: int
    last_seen: int
    velocity_x: int
    velocity_y: int


def draw_balls(
    balls: List[Ball],
    frame: cv.Mat,
    color: Tuple[int, int, int] = (0, 255, 255),
    thickness: int = 2,
) -> None:
    for ball in balls:
        cv.circle(frame, ball.position, int(ball.radius), color, thickness)


def detect_balls(mask, frame_count) -> List[Ball]:
    balls: List[Ball] = []
    cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        area = cv.contourArea(c)
        perimeter = cv.arcLength(c, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter)

        if circularity > 0.8:
            (_, radius) = cv.minEnclosingCircle(c)

            M = cv.moments(c)  # per calcolare il centro del cerchio
            center = (
                (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if M["m00"] != 0
                else None
            )

            balls.append(
                Ball(
                    position=center,
                    radius=radius,
                    last_seen=frame_count,
                    velocity_x=0,
                    velocity_y=0,
                )
            )

    return balls


def check_ball_movement(
    previous_balls: List[Ball],
    current_balls: List[Ball],
    movement_threshold: float = 2.0,
) -> bool:
    for ball in current_balls:
        nearest_prev_ball = {"ball": None, "distance": float("inf")}

        for p_ball in previous_balls:
            d = euclidean(ball.position, p_ball.position)
            if d < nearest_prev_ball["distance"]:
                nearest_prev_ball["distance"] = d
                nearest_prev_ball["ball"] = p_ball

        if (
            nearest_prev_ball["distance"] > movement_threshold
            and nearest_prev_ball["ball"] is not None
        ):
            return True

        if nearest_prev_ball["ball"] is not None:
            previous_balls.remove(nearest_prev_ball["ball"])

    return False
