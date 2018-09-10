FROM ubuntu:16.04

WORKDIR /srv

RUN apt-get update &&\
  apt-get install -y python3 git apt-transport-https curl &&\
  curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - &&\
  touch /etc/apt/sources.list.d/kubernetes.list &&\
  echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list &&\
  apt update &&\
  apt install -y kubectl

COPY httpd.py /srv

CMD python3 httpd.py 25565
