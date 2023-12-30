import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer, EmployeeDetailSerializer
from rest_framework.permissions import AllowAny 

# Set up logging
logger = logging.getLogger(__name__)

class EmployeeListCreateView(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListCreateView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskAssignView(APIView):
    def post(self, request):
        lead_id = request.data.get('lead_id')
        subordinate_id = request.data.get('subordinate_id')
        tasks = request.data.get('tasks', [])

        try:
            assigning_lead = Employee.objects.get(id=lead_id, is_lead=True)
        except Employee.DoesNotExist:
            logger.error(f"Lead not found with ID: {lead_id}")
            return Response({"error": "Lead not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            subordinate_employee = Employee.objects.get(id=subordinate_id, is_lead=False)
        except Employee.DoesNotExist:
            logger.error(f"Subordinate employee not found with ID: {subordinate_id}")
            return Response({"error": "Subordinate employee not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate that tasks are not assigned to the same employee more than once
        for task_id in tasks:
            if subordinate_employee.tasks.filter(id=task_id).exists():
                logger.warning(f"Task with ID {task_id} already assigned to the employee.")
                return Response({"error": "Task already assigned to the employee"}, status=status.HTTP_400_BAD_REQUEST)

        task_serializer = TaskSerializer(data=request.data)
        if task_serializer.is_valid():
            new_task = task_serializer.save()

            # Use set() to update the tasks for the subordinate employee
            subordinate_employee.tasks.set(tasks)

            # Retrieve the assigned employee details
            assigned_employee_details = EmployeeDetailSerializer(subordinate_employee).data

            # Log the task assignment
            logger.info(f"Tasks assigned successfully by lead {assigning_lead.id} to subordinate {subordinate_employee.id}")

            response_data = {
                "success": "Tasks assigned successfully",
                "assigned_employee": assigned_employee_details
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        # Log if task serialization fails
        logger.error(f"Task serialization failed: {task_serializer.errors}")
        return Response(task_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeDetailView(APIView):
    def get(self, request, pk):
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            logger.error(f"Employee not found with ID: {pk}")
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeDetailSerializer(employee)
        return Response(serializer.data)

class TaskUnassignView(APIView):
    permission_classes = [AllowAny]  # AllowAny allows unauthenticated access

    def delete(self, request, pk):
        try:
            task = Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response({"error": f"Task with id {pk} not found"}, status=status.HTTP_404_NOT_FOUND)

        assigned_employees = task.assigned_to.all()

        # Check if any assigned employee is also a lead
        if any(employee.is_lead for employee in assigned_employees):
            return Response({"error": "Leads cannot be unassigned tasks"}, status=status.HTTP_403_FORBIDDEN)

        
        task.delete()

        # Retrieve the remaining tasks after unassigning
        remaining_tasks = TaskSerializer(Task.objects.all(), many=True).data

        response_data = {
            "success": "Task unassigned successfully",
            "remaining_tasks": remaining_tasks
        }

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
