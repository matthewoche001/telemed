from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False)
        return {
            'unread_count': unread_notifications.count(),
            'recent_notifications': unread_notifications[:5]
        }
    return {}
