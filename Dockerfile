FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN python main.py prerequisites

EXPOSE 5672

CMD ["python3", "run_comsuming.py"]