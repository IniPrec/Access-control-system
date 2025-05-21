import cv2

def capture_face():
    cam = cv2.VideoCapture(0)
    print("Capturing image... Look at the camera.")
    ret, frame = cam.read()
    if ret:
        cv2.imwrite("captured.jpg", frame)
    cam.release()
    return "captured.jpg"