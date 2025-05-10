from django.urls import path
from tasks.views import TaskCRUDView

urlpatterns = [
    path('task/', TaskCRUDView.as_view(), name='tasks-crud'),
]