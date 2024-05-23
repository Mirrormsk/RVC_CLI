FROM python:3.9

WORKDIR /app

COPY . /app

RUN apt update

RUN apt install -y ffmpeg

RUN pip install -r requirements.txt

RUN python main.py prerequisites

