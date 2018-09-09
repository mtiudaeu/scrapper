FROM ubuntu:16.04

WORKDIR /srv

RUN apt-get update &&\
  apt-get install -y python3

COPY httpd.py /srv

CMD python3 httpd.py 25565
