FROM tiangolo/uvicorn-gunicorn:python3.9
WORKDIR /app
RUN pwd
RUN ls
COPY requirements.txt cert.pem key.pem /app
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY app /app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile","key.pem", "--ssl-certfile", "cert.pem"]