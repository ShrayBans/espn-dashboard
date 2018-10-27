FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN pip3 install flask
RUN pip3 install flask_restful
RUN pip3 install ranking
RUN pip3 install pandas
RUN pip3 install requests

COPY . /app
WORKDIR /app

CMD ["python3", "src/app.py"]