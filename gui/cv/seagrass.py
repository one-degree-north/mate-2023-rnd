import cv2
import numpy as np

class Seagrass:
    def __init__(self):
        self.contrast = 1
        self.brightness = 1

    def change(self, before, after):
        return after - before
        
    def healed_seagrass(self, img):
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        adjust = cv2.convertScaleAbs(img_hsv, beta=self.contrast, alpha=self.brightness)

        blurred = cv2.GaussianBlur(adjust, (3,3), 0)

        lower = np.array([50,70,70])
        upper = np.array([200,255,200])

        mask = cv2.inRange(blurred, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        img_contours = img.copy()
        cv2.drawContours(img_contours, contours, -1, (0, 0, 255), 2)

        return len(contours), img_contours


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        grass = Seagrass()

        count, frame_contours = grass.detect_contours(frame)

        print(count)
        cv2.imshow("seagrass", frame_contours)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
