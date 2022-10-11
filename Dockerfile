FROM python:3.10.7

WORKDIR /app

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY . /app

ENTRYPOINT ["python"]
CMD ["app.py"]