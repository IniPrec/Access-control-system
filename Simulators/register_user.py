import cv2
import requests
import random
import string

# === CONFIG ===
API_URL = "http://127.0.0.1:8000/api/users/"
PHOTO_FILENAME = "captured_photo.jpg"

# === Generate Random RFID Tag ===
def generate_rfid(length=10):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

# === Capture Image from Webcam ===
def capture_image(filename=PHOTO_FILENAME):
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        print("Failed to grab frame.")
        return None
    cv2.imshow("Captured Image", frame)
    cv2.imwrite(filename, frame)
    cv2.waitKey()
    cam.release()
    cv2.destroyAllWindows()
    print(f"Image saved to {filename}")
    return filename

# === Send to Django API ===
def register_user(full_name, rfid_tag, role, photo_path):
    with open(photo_path, "rb") as img:
        files = {"photo": img}
        data = {
            "full_name": full_name,
            "rfid_tag": rfid_tag,
            "role": role
        }
        response = requests.post(API_URL, data=data, files=files)
        if response.status_code == 201:
            print("User registered successfully!")
            print(response.json())
        else:
            print("Failed to register user.")
            print(response.status_code, response.text)

# === MAIN FLOW ===
if __name__ == "__main__":
    name = input("Enter full name: ")
    role = input("Enter role (default: User): ") or "User"
    rfid_tag = generate_rfid()
    print(f"Generated RFID Tag: {rfid_tag}")

    image_path = capture_image()
    if image_path:
        register_user(name, rfid_tag, role, image_path)