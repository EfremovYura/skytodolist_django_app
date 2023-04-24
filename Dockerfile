FROM c

WORKDIR /opt

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# ENTRYPOINT ["bash", "entrypoint.sh"]

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "127.0.0.1:8000"]
