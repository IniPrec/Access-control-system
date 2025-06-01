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
    if status == 'access_granted':
        logs = logs.filter(access_granted=True)
    elif status == 'failure':
        logs = logs.filter(access_granted=False)

    role = request.GET.get('role')
    if role:
        logs = logs.filter(user__role=role)

    total_logs = logs.count()
    successful_logs = logs.filter(access_granted=True).count()
    failed_logs = logs.filter(access_granted=False).count()

    return render(request, 'core/access_logs.html', {
        'logs': logs,
        'total_logs': total_logs,
        'successful_logs': successful_logs,
        'failed_logs': failed_logs,
    })

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
            return redirect('user_dashboard') # Go to face check

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

    # Load registered photo
    known_image = face_recognition.load_image_file(user.photo.path)
    known_encodings = face_recognition.face_encodings(known_image)

    if not known_encodings:
        log_access(user,user.rfid_tag, False, reason="No face in registered photo")
        messages.error(request, "No face detected in the registered photo.")
        return redirect('biometric_login')

    # Start Camera
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("Camera opened:", cap.isOpened())

    frame = None
    for _ in range(10):
        ret, temp = cap.read()
        if ret:
            frame = temp
    cap.release()

    if frame is None:
        log_access(user, user.rfid_tag, False, reason="Camera failure")
        messages.error(request, "Failed to capture image from camera.")
        return redirect("biometric_login")

    # if ret:
        #cv2.imshow("Face Capture - Press any key to continue", frame)
        #cv2.waitKey(5000)
        #cv2.destroyAllWindows()

    captured_path = os.path.join(settings.MEDIA_ROOT, 'captured', f"{user.rfid_tag}_verify.jpg")
    os.makedirs(os.path.dirname(captured_path), exist_ok=True)
    cv2.imwrite(captured_path, frame)
    cv2.imwrite("media/captured_debug.jpg", frame)

    request.session['captured_preview'] = f"/media/captured/{user.rfid_tag}_verify.jpg"

    # Encode captured face
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype('uint8')
    face_locations = face_recognition.face_locations(rgb_frame)
    if not face_locations:
        log_access(user, user.rfid_tag, False, reason="No face in captured image")
        messages.error(request, "No face detected in the captured image.")
        return redirect('biometric_login')
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)


    print("Detected faces in verification image:", len(face_encodings))

    if not face_encodings:
            log_access(user, user.rfid_tag, False, reason="No face in captured image")
            messages.error(request, "No face detected in the captured image.")
            return redirect('biometric_login')

    # Match faces
    match_found = any(face_recognition.compare_faces([known_encodings[0]], encoding)[0]
                      for encoding in face_encodings)

    if match_found:
        log_access(user, user.rfid_tag, True, reason="Face match")
        request.session['verification_result'] = 'success'
    else:
        log_access(user, user.rfid_tag, False, reason="Face mismatch")
        request.session['verification_result'] = 'fail'

    return redirect('verify-result')

def verify_result(request):
    user_id = request.session.get('login_user_id')
    captured_preview = request.session.get('captured_preview')
    result = request.session.get('verification_result')

    user = User.objects.get(id=user_id)

    return render(request, 'core/verify_result.html', {
        'user': user,
        'captured_preview': captured_preview,
        'result': result
    })

def user_dashboard(request):
    user_id = request.session.get('login_user_id')
    user = User.objects.get(id=user_id)
    logs = AccessLog.objects.filter(user=user).order_by('-timestamp')

    return render(request, 'core/user_dashboard.html', {
        'user': user,
        'logs': logs
    })

def login_view(request):
    result = None
    captured_path = ""
    ret = False

    if request.method =='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            rfid_tag = form.cleaned_data['rfid_tag']
            try:
                user = User.objects.get(rfid_tag=rfid_tag)

                # Capture face with webcam
                cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                frame = None
                for _ in range(10):
                    ret, temp = cam.read()
                    if ret:
                        frame = temp
                cam.release()

                if frame is None:
                    result = "Failed to capture image."
                    log_access(user, rfid_tag, False, reason="Camera failure")
                    return render(request, 'core/login.html', {
                        'form': form,
                        'result': result
                    })

                # if ret:
                    # cv2.imshow("Face Capture", frame) # Shows webcam preview
                    # cv2.waitKey(10000) # Wait 10 seconds
                    # cv2.destroyAllWindows()
                os.makedirs('media/captured', exist_ok=True)
                captured_path = f"media/captured/{user.rfid_tag}_login.jpg"
                cv2.imwrite(captured_path, frame)
                cv2.imwrite("media/captured_debug.jpg", frame)

                # Load and encode known user photo
                known_image = face_recognition.load_image_file(user.photo.path)
                known_encodings = face_recognition.face_encodings(known_image)

                # Load and encode captured photo
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype('uint8')
                face_locations = face_recognition.face_locations(rgb_frame)
                if not face_locations:
                    log_access(user, rfid_tag, False, reason="No face in captured image")
                    result = "No face detected in the captured image."
                    return render(request, 'core/login.html', {
                        'form': form,
                        'result': result
                    })
                test_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                print("Detected faces in login image:", len(test_encodings))

                if known_encodings and test_encodings:
                    match = face_recognition.compare_faces([known_encodings[0]], test_encodings[0], tolerance=0.4)[0]
                    if match:
                        log_access(user, rfid_tag, True, reason="Face match")
                        request.session['login_user_id'] = user.id
                        request.session['verification_result'] = 'success'

                        if user.role == 'admin':
                            return redirect('user-list')
                        else:
                            return redirect('user_dashboard')
                            # AccessLog.objects.create(
                                # user=user,
                                # rfid_tag=rfid_tag,
                                # access_granted=True,
                                # reason="Face match",
                                # timestamp=timezone.now()
                            # )
                            # result = f"Access granted. Welcome, {user.full_name}!"
                    else:
                        log_access(user, rfid_tag, False, reason="Face mismatch")
                        result = "Face does not match. Access denied."
                            # AccessLog.objects.create(
                                # user=user,
                                # rfid_tag=rfid_tag,
                                # access_granted=False,
                                # reason="Face mismatch",
                                # timestamp=timezone.now()
                            # )
                            # result = "Face does not match. Access denied."
                else:
                    log_access(user, rfid_tag, False, reason="Could not detect face properly.")
                    result = "Could not detect face properly."
            except User.DoesNotExist:
                result = "No user found with that RFID tag."
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

# def delete_user(request, user_id):
    # user = get_object_or_404(User, id=user_id)
    # user.delete()
    # messages.success(request, f"{user.full_name} deleted.")
    # return redirect('user-list')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class AccessLogViewSet(viewsets.ModelViewSet):
    queryset = AccessLog.objects.all()
