# from django.shortcuts import render, redirect
# from .models import Task
# from .forms import TaskForm
# from django.http import HttpResponse
# from prometheus_client import generate_latest, REGISTRY, Counter, Histogram

# # Define Prometheus metrics
# TASK_CREATED_COUNTER = Counter('tasks_created_total', 'Total number of tasks created')
# TASK_UPDATED_COUNTER = Counter('tasks_updated_total', 'Total number of tasks updated')
# TASK_DELETED_COUNTER = Counter('tasks_deleted_total', 'Total number of tasks deleted')

# # To list all the tasks
# def task_list(request):
#     tasks = Task.objects.all()
#     form = TaskForm()
#     if request.method == 'POST':
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             form.save()
#             TASK_CREATED_COUNTER.inc()  # Increment the created tasks counter
#             return redirect("task_list")
#     context = {"tasks": tasks, "form": form}
#     return render(request, "task_list.html", context)

# # To update the tasks
# def task_update(request, pk):
#     task = Task.objects.get(id=pk)
#     form = TaskForm(instance=task)
#     if request.method == 'POST':
#         form = TaskForm(request.POST, instance=task)
#         if form.is_valid():
#             form.save()
#             TASK_UPDATED_COUNTER.inc()  # Increment the updated tasks counter
#             return redirect('task_list')
#     context = {"form": form}
#     return render(request, "task_update.html", context)

# # To delete the task
# def task_delete(request, pk):
#     task = Task.objects.get(id=pk)
#     if request.method == 'POST':
#         task.delete()
#         TASK_DELETED_COUNTER.inc()  # Increment the deleted tasks counter
#         return redirect('task_list')
#     context = {"task": task}
#     return render(request, "task_delete.html", context)

# # Create a Metrics Endpoint
# def metrics(request):
#     return HttpResponse(generate_latest(REGISTRY), content_type='text/plain')

from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm
from django.http import HttpResponse
from prometheus_client import generate_latest, REGISTRY, Counter

# Define Prometheus metrics
TASK_CREATED_COUNTER = Counter('tasks_created_total', 'Total number of tasks created')
TASK_UPDATED_COUNTER = Counter('tasks_updated_total', 'Total number of tasks updated')
TASK_DELETED_COUNTER = Counter('tasks_deleted_total', 'Total number of tasks deleted')

# To list all the tasks
def task_list(request):
    tasks = Task.objects.all()
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)  # Accepting files in the form
        if form.is_valid():
            form.save()  # This will save the file to S3 automatically
            TASK_CREATED_COUNTER.inc()  # Increment the created tasks counter
            return redirect("task_list")
    context = {"tasks": tasks, "form": form}
    return render(request, "task_list.html", context)

# To update the tasks
def task_update(request, pk):
    task = Task.objects.get(id=pk)
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)  # Include files for updates
        if form.is_valid():
            form.save()  # Update will handle S3 storage
            TASK_UPDATED_COUNTER.inc()  # Increment the updated tasks counter
            return redirect('task_list')
    context = {"form": form}
    return render(request, "task_update.html", context)

# To delete the task
def task_delete(request, pk):
    task = Task.objects.get(id=pk)
    if request.method == 'POST':
        task.delete()
        TASK_DELETED_COUNTER.inc()  # Increment the deleted tasks counter
        return redirect('task_list')
    context = {"task": task}
    return render(request, "task_delete.html", context)

# Create a Metrics Endpoint
def metrics(request):
    return HttpResponse(generate_latest(REGISTRY), content_type='text/plain')
