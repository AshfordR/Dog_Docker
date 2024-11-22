FROM python:3.12

WORKDIR /app

COPY . .

RUN apt update
RUN  pip install -r requirements.txt
RUN pip install flask

CMD ["python","run.py"]
