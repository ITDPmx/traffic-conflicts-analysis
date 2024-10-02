# service2/Dockerfile
FROM ultralytics/yolov5:latest

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

# Set the working directory
WORKDIR /app

# Copy the Generic folder to the parent directory of /app
COPY Generic /app/../Generic

# Copy the rest of the application files to /app
COPY . /app

# Expose the port the app runs on
EXPOSE 8001

CMD ["python", "main.py"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
