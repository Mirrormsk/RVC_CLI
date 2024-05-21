FROM python:3.9

WORKDIR /app

COPY install.sh /app/install.sh

RUN chmod +x install.sh

COPY . /app

RUN python main.py prerequisites

RUN ./install.sh

EXPOSE 5672

CMD ["python3", "run_comsuming.py"]