import cv2 as cv
import numpy as np

H_DIFF, S_DIFF, V_DIFF = 5, 10, 5


def create_mask(frame_hsv, points, table_colors):
    """
    Creates a mask to remove specific color ranges within a defined region.

    This function takes an HSV image (OpenCV format), a set of points defining a polygon,
    and a list of colors of the table. It creates a mask that combines two filters:

    1. A polygon mask based on the given points
    2. A color range mask based on the provided table colors

    Args:
        frame_hsv (MatLike): Frame da cui ricavare la maschera. Deve essere in formato HSV (OpenCV format)

        points (List[Tuple(int, int)]): I 4 punti (x,y) che descrivono il rettangolo che delimita il tavolo da gioco. I punti devono essere ordinati in senso orario.

        table_colors (List[Tuple(int,int,int)]): Un array di colori scritti in HSV (OpenCV format) che descrivono il tavolo da gioco

    Returns:
        MatLike: _description_
    """
    color_lower = tuple(
        min(color[i] for color in table_colors) - diff
        for i, diff in enumerate([H_DIFF, S_DIFF, V_DIFF])
    )
    color_upper = tuple(
        max(color[i] for color in table_colors) + diff
        for i, diff in enumerate([H_DIFF, S_DIFF, V_DIFF])
    )

    rec_mask = cv.fillPoly(np.zeros(frame_hsv.shape[:2], dtype=np.uint8), [points], 255)
    color_mask = cv.bitwise_not(cv.inRange(frame_hsv, color_lower, color_upper))
    color_mask = cv.erode(color_mask, None, iterations=3)
    color_mask = cv.dilate(color_mask, None, iterations=2)

    return cv.bitwise_and(color_mask, rec_mask)
