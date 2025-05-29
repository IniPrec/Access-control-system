from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from .models import User, AccessLog
from .serializers import UserSerializer, AccessLogSerializer
from .forms import UserRegistrationForm, LoginForm
from .utils import generate_rfid
from django.contrib import messages
import cv2
import face_recognition
import os
import base64
from django.core.files.base import ContentFile
from access_control_system import settings

def user_list(request):
    users = User.objects.all()
    return render(request, 'core/user_list.html', {'users': users})

def access_log_list(request):
    logs = AccessLog.objects.select_related('user').order_by('-timestamp')

    # Filter by RFID
    rfid_query = request.GET.get('rfid')
    if rfid_query:
        logs = logs.filter(rfid_tag__icontains=rfid_query)

    # Filter by success/failure
    status = request.GET.get('status')
    if status == 'True':
        logs = logs.filter(access_granted=True)
    elif status == 'False':
        logs = logs.filter(access_granted=False)

    return render(request, 'core/access_logs.html', {'logs': logs})

def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES) # Handles form submission
        if form.is_valid():
            user = form.save(commit=False) # Saves the new user to the database

            image_data = request.POST.get('captured_image')

            # Check if neither method was used
            if not request.FILES.get('photo') and not image_data:
                form.add_error('photo', "You must upload a photo or capture one using the webcam.")
                return render(request, 'core/user_register.html', {'form': form})

            # If no upload, but image_data exists, use webcam
            if not user.photo and image_data:
                format, imgstr = image_data.split(';base64,')
                image_file = ContentFile(base64.b64decode(imgstr), name=f"{user.rfid_tag}_webcam.jpg")
                user.photo = image_file # Assign webcam image 

            user.save()
            # Redirect to Face verification after registration
            request.session['login_user_id'] = user.id # Store user in session
            return redirect('face_verification') # Go to face check

    else:
        rfid = generate_rfid()
        form = UserRegistrationForm(initial={'rfid_tag': rfid}) # Creates an empty form instance
        
    return render(request, 'core/user_register.html', {'form': form})

def biometric_login(request):
    if request.method == 'POST':
        rfid_tag = request.POST.get('rfid_tag')
        try:
            user = User.objects.get(rfid_tag=rfid_tag)
            request.session['login_user_id'] = user.id # temporarily store ID
            return redirect('face_verification')
        except User.DoesNotExist:
            messages.error(request, 'RFID not found')
    return render(request, 'core/biometric_login.html')

def face_verification(request):
    user_id = request.session.get('login_user_id')
    if not user_id:
        return redirect('biometric_login')
    
    user = User.objects.get(id=user_id)

    # Load the stored photo
    known_image = face_recognition.load_image_file(user.photo.path)
    known_encodings = face_recognition.face_encodings(known_image)

    if not known_encodings:
        log_access(user,user.rfid_tag, False, reason="No face in registered photo")
        messages.error(request, "No face detected in the registered photo.")
        return redirect('biometric_login')

    # Start Camera
    cap = cv2.VideoCapture(0)

    # Let camera warm up for a few frames
    for _ in range(5):
        cap.read()
    
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        log_access(user, user.rfid_tag, False, reason="Camera failure")
        messages.error(request, "Failed to capture image from camera.")
        return redirect("biometric_login")

    if ret:
        #cv2.imshow("Face Capture - Press any key to continue", frame)
        #cv2.waitKey(5000)
        #cv2.destroyAllWindows()

        captured_path = os.path.join(settings.MEDIA_ROOT, 'captured', f"{user.rfid_tag}_verify.jpg")
        os.makedirs(os.path.dirname(captured_path), exist_ok=True)
        cv2.imwrite(captured_path, frame)

        request.session['captured_preview'] = f"/media/captured/{user.rfid_tag}_verify.jpg"

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        if not face_encodings:
            log_access(user, user.rfid_tag, False, reason="No face in captured image")
            messages.error(request, "No face detected in the captured image.")
            return redirect('biometric_login')

        match_found = False

        for face_encoding in face_encodings:
            match = face_recognition.compare_faces([known_encodings[0]], face_encoding)[0]
            if match:
                match_found = True
                break # Exit early on first match

        # Log and respond outside the loop
        if match_found:
            log_access(user, user.rfid_tag, True, reason="Face match")
            request.session['verification_result'] = 'success'
        else:
            log_access(user, user.rfid_tag, False, reason="Face mismatch")
            request.session['verifaction_result'] = 'fail'

        return redirect('verify-result')

        messages.error(request, "❌ Face does not match.")
    else:
        messages.error(request, "❌ Failed to capture image from camera.")

    return redirect('biometric_login')

def verify_result(request):
    user_id = request.session.get('login_user_id')
    captured_preview = request.session.get('captured_preview')
    result = request.session.get('verification_result')

    user = User.objects.get(id=user_id)

    return render(request, 'core/verify_result.html', {
        'user': user,
        'captured+preview': captured_preview,
        'result': result
    })

def user_dashboard(request):
    user_id = request.session.get('login_user_id')
    user = User.objects.get(id=user_id)
    logs = AccessLog.objects.filter(user=user).order_by('-timestamp')

    return render(request, 'core/dashboard.html', {
        'user': user,
        'logs': logs
    })


def login_view(request):
    result = None

    if request.method =='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            rfid_tag = form.cleaned_data['rfid_tag']
            try:
                user = User.objects.get(rfid_tag=rfid_tag)

                # Capture face with webcam
                cam = cv2.VideoCapture(0)
                ret, frame = cam.read()

                if ret:
                    cv2.imshow("Face Capture", frame) # Shows webcam preview
                    cv2.waitkey(10000) # Wait 10 seconds
                    cv2.destroyAllWindows()
                    os.makedirs('media/captured', exist_ok=True)
                    captured_path = f"media/captured/{user.rfid_tag}_login.jpg"
                    cv2.imwrite(captured_path, frame)

                    # Load and encode known user photo
                    known_image = face_recognition.load_image_file(user.photo.path)
                    known_encodings = face_recognition.face_encodings(known_image)

                    # Load and encode captured photo
                    test_image = face_recognition.load_image_file(captured_path)
                    test_encodings = face_recognition.face_encodings(test_image)

                    if known_encodings and test_encodings:
                        match = face_recognition.compare_faces([known_encodings[0]], test_encodings[0])[0]
                        if match:
                            AccessLog.objects.create(
                                user=user,
                                rfid_tag=rfid_tag,
                                access_granted=True,
                                reason="Face match",
                                timestamp=timezone.now()
                            )
                            result = f"Access granted. Welcome, {user.full_name}!"
                        else:
                            AccessLog.objects.create(
                                user=user,
                                rfid_tag=rfid_tag,
                                access_granted=False,
                                reason="Face mismatch",
                                timestamp=timezone.now()
                            )
                            result = "Face does not match. Access denied."
                    else:
                        result = "Could not detect face properly."
                else:
                    result = "Failed to capture image."
            except User.DoesNotExist:
                result = "NO user found with that RFID tag."
    else:
        form = LoginForm()

    return render(request, 'core/login.html', {'form': form, 'result': result, 'captured_path': captured_path.replace("media/", "/media/") if ret else None})

def log_access(user, rfid, access_granted, reason=None):
    AccessLog.objects.create(
        user=user,
        rfid_tag=rfid,
        access_granted=access_granted,
        reason=reason,
        timestamp=timezone.now()
    )

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"{user.full_name} deleted.")
    return redirect('user-list')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AccessLogViewSet(viewsets.ModelViewSet):
    queryset = AccessLog.objects.all()
    serializer_class = AccessLogSerializer