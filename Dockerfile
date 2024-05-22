FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN python main.py prerequisites

