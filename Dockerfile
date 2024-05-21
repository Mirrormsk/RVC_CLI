FROM python:3.9

WORKDIR /app

COPY . /app

RUN python main.py prerequisites

RUN pip install -r requirements.txt

EXPOSE 5672

CMD ["python3", "run_comsuming.py"]