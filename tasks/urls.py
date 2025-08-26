from django.urls import path
from tasks.views import TaskCRUDView,MilestoneView

urlpatterns = [
    path('task/', TaskCRUDView.as_view(), name='tasks-crud'),
    path('milestone/', MilestoneView.as_view(), name='milestone-crud'),
]