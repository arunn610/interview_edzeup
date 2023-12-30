from django.urls import path
from .views import EmployeeListCreateView, TaskListCreateView, TaskAssignView, TaskUnassignView

urlpatterns = [
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/assign/', TaskAssignView.as_view(), name='task-assign'),
    path('tasks/unassign/<int:pk>/', TaskUnassignView.as_view(), name='task-unassign'),
]
