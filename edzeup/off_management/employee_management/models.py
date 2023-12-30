from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_lead = models.BooleanField(default=False)
    tasks = models.ManyToManyField('Task', related_name='assigned_to')

    def __str__(self):
        return f"{self.name} ({self.email})"

class Task(models.Model):
    title = models.CharField(max_length=255)
    deadline = models.DateField()

    def __str__(self):
        return self.title
