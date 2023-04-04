FROM python:3.11-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["bash", "entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]
