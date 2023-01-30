import cv2
import numpy as np

def detect_contours(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blurred = cv2.GaussianBlur(img_hsv, (3,3), 0)

    lower = np.array([50,70,70])
    upper = np.array([200,255,200])

    mask = cv2.inRange(blurred, lower, upper)
    contours, h = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    img_contours = img.copy()
    cv2.drawContours(img_contours, contours, -1, (0, 0, 255), 1)

    return len(contours), img_contours


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        frame_contours = detect_contours(frame)

        cv2.imshow("seagrass", frame_contours[1])

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
