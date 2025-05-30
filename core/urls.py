from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AccessLogViewSet, user_register, user_list, biometric_login, face_verification, verify_result, delete_user, deleted_users_list, restore_user

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'logs', AccessLogViewSet)

urlpatterns = router.urls # exposes /users/ and /logs/ under wherever it's included

urlpatterns = [
    path('register/', user_register, name='user-register'),
    path('users/', user_list, name='user-list'),
    path('login/', biometric_login, name='biometric_login'),
    path('verify-face/', face_verification, name='face_verification'),
    path('verify-result/', verify_result, name='verify-result'),
    path('delete-user/<int:user_id>/', delete_user, name='delete-user'),
    path('deleted-users/', deleted_users_list, name='deleted-users'),
    path('restored-user/<int:user_id>/', restore_user, name='restore-user'),
]