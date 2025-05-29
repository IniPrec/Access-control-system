import csv
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_control_system.settings')
django.setup()

from core.models import AccessLog

with open('access_log_report.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['User', 'RFID', 'Granted', 'Reason', 'Timestamp'])

    for log in AccessLog.objects.all():
        user_name = log.user.full_name if log.user else "Deleted User"
        writer.writerow([
            user_name,
            log.rfid_tag,
            log.access_granted,
            log.reason,
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])

print("Logs exported to access_log_report.csv")