FROM ubuntu

RUN apt update
RUN apt install python3-pip -y
RUN  pip install -r requirements.txt
RUN pip install flask


WORKDIR /app

COPY . .

CMD ["python3","-m","flask","app","--host=0.0.0.0"]
