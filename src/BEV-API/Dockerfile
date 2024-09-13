FROM tensorflow/tensorflow:1.13.1-gpu-py3

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . /app

WORKDIR /app

EXPOSE 8000


CMD ["python", "main.py"]

