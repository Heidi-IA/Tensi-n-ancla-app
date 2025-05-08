FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
docker build -t mi_app .
docker run -p 5000:5000 mi_app
