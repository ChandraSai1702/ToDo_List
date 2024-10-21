from django.shortcuts import render, redirect
from .models import Task
from .forms import TaskForm
from django.http import HttpResponse
from prometheus_client import generate_latest, REGISTRY, Counter
import json
import boto3
from django.conf import settings

# Define Prometheus metrics
TASK_CREATED_COUNTER = Counter('tasks_created_total', 'Total number of tasks created')
TASK_UPDATED_COUNTER = Counter('tasks_updated_total', 'Total number of tasks updated')
TASK_DELETED_COUNTER = Counter('tasks_deleted_total', 'Total number of tasks deleted')

# AWS Configuration
AWS_S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
AWS_REGION = settings.AWS_S3_REGION_NAME
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def save_tasks_to_s3():
    """Save each task as a separate JSON file in S3."""
    try:
        tasks = Task.objects.all()
        
        for task in tasks:
            task_data = {
                'id': task.id,
                'title': task.title,
                'completed': task.completed,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'updated_at': task.updated_at.isoformat() if task.updated_at else None
            }
            task_json = json.dumps(task_data)
            
            # Store each task as a separate file using the task ID
            s3_client.put_object(
                Bucket=AWS_S3_BUCKET,
                Key=f'tasks/{task.id}.json',
                Body=task_json
            )
        
        print("Tasks saved to S3 successfully.")
    except Exception as e:
        print(f"Error uploading tasks to S3: {e}")

def load_tasks_from_s3():
    """Load tasks from S3 and restore them to the database."""
    try:
        # List all objects with the 'tasks/' prefix in the bucket
        response = s3_client.list_objects_v2(
            Bucket=AWS_S3_BUCKET,
            Prefix='tasks/'
        )
        
        # Clear existing tasks before loading from S3
        Task.objects.all().delete()
        
        # Iterate through each object in the response
        for obj in response.get('Contents', []):
            task_key = obj['Key']
            task_response = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=task_key)
            task_json = task_response['Body'].read().decode('utf-8')
            task_data = json.loads(task_json)
            
            # Create task in the database from the JSON data
            Task.objects.create(
                id=task_data['id'],
                title=task_data['title'],
                completed=task_data['completed'],
                created_at=task_data['created_at'],
                updated_at=task_data['updated_at']
            )
        
        print("Tasks loaded from S3 successfully.")
    except s3_client.exceptions.NoSuchKey:
        print("No tasks found in S3, starting fresh.")
    except Exception as e:
        print(f"Error loading tasks from S3: {e}")

# To list all the tasks
def task_list(request):
    # Load tasks from S3 each time the task list is accessed (optional)
    load_tasks_from_s3()
    
    tasks = Task.objects.all()
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            save_tasks_to_s3()  # Save the updated task list to S3
            TASK_CREATED_COUNTER.inc()  # Increment the created tasks counter
            return redirect("task_list")
    context = {"tasks": tasks, "form": form}
    return render(request, "task_list.html", context)

def task_update(request, pk):
    task = Task.objects.get(id=pk)
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            
            # Save the updated task to S3
            try:
                task_data = {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                s3_client.put_object(
                    Bucket=AWS_S3_BUCKET,
                    Key=f'tasks/{task.id}.json',
                    Body=json.dumps(task_data)
                )
                print(f"Task {task.id} updated in S3.")
            except Exception as e:
                print(f"Error updating task {task.id} in S3: {e}")

            TASK_UPDATED_COUNTER.inc()  # Increment the updated tasks counter
            return redirect('task_list')

    context = {"form": form}
    return render(request, "task_update.html", context)


# To delete the task
def task_delete(request, pk):
    task = Task.objects.get(id=pk)
    if request.method == 'POST':
        task.delete()
        try:
            s3_client.delete_object(
                Bucket=AWS_S3_BUCKET,
                Key=f'tasks/{pk}.json'
            )
            print(f"Task {pk} deleted from S3.")
        except Exception as e:
            print(f"Error deleting task {pk} from S3: {e}")

        save_tasks_to_s3()  # Save the updated task list to S3
        TASK_DELETED_COUNTER.inc()  # Increment the deleted tasks counter
        return redirect('task_list')
    context = {"task": task}
    return render(request, "task_delete.html", context)

# Create a Metrics Endpoint
def metrics(request):
    return HttpResponse(generate_latest(REGISTRY), content_type='text/plain')
