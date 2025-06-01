from django.urls import path
from .views import NotificationListView, NotificationMarkReadView, UnreadCountView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('unread-count/', UnreadCountView.as_view(), name='unread-count'),
]