import cv2
import requests
import time

# === CONFIG ===
BASE_URL = "http://127.0.0.1:8000/api/"
USERS_ENDPOINT = BASE_URL + "users/"
LOGS_ENDPOINT = BASE_URL + "logs/"
CAPTURE_IMAGE = True # Set to True to capture webcam photo

# === Look up user by RFID tag ===
def get_user_by_rfid(rfid_tag):
    response = requests.get(USERS_ENDPOINT, params={"rfid_tag": rfid_tag})
    if response.status_code == 200:
        users = response.json()
        if users:
            return users[0] # return first matching user
    return None

# === Optional Webcam Capture for Verification ===
def capture_image():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not ret:
        print("Failed to capture image.")
        return
    cv2.imshow("Captured for Verification", frame)
    cv2.waitKey(1000)
    cam.release()
    cv2.destroyAllWindows()
    print("Image captured (not uploaded).")

# === Log Access Attempt ===
def log_access(user_id, granted, method = "RFID"):
    payload = {
        "user": user_id,
        "access_granted": granted,
        "method": method
    }
    response = requests.post(LOGS_ENDPOINT, json=payload)
    if response.status_code == 201:
        print("Access log saved!")
    else:
        print("Failed to log access.")
        print(response.status_code, response.text)

# === MAIN FLOW ===
if __name__ == "__main__":
    print("🔐 Simulated RFID Access")
    tag = input("Scan RFID Tag (or paste one): ")

    print("🔎 Looking up user...")
    user = get_user_by_rfid(tag)
    if user:
        print(f"✅ User found: {user['full_name']} ({user['role']})")

        if CAPTURE_IMAGE:
            capture_image()

        confirm = input("Grant access? (y/n): ").lower()
        granted = confirm == "y"
        log_access(user["id"], granted)
    else:
        print("❌ No user found with that RFID.")