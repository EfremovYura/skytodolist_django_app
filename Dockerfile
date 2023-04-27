FROM python:3.11

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "migrate"]

CMD ["python", "manage.py", "collectstatic", "-c", "--no-input"]

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
