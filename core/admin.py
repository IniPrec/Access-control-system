from django.contrib import admin
from .models import User, AccessLog

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'rfid_tag', 'role', 'created_at')

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('rfid_tag', 'user', 'access_granted', 'timestamp', 'reason')
    list_filter = ('access_granted', 'timestamp', 'user')
    searc_fields = ('rfid_tag', 'user__full_name')