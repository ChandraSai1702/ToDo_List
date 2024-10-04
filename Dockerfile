# USE OFFICIAL PYTHON IMAGE
FROM python:3.10

# set the working directory inside the container
WORKDIR /app

# copy the requirements file to install dependencies
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt


# copy the entire django project into the container
COPY . /app/

# run django collectstatic
RUN python manage.py collectstatic --noinput

# Ensure the migration runs when the container starts
RUN chmod +x /app/entrypoint.sh

# Set the default entrypoint to automatically run migrations and start the server
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000

# set the default command to run django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]