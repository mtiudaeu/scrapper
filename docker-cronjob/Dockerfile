FROM ubuntu:16.04

RUN apt update &&\
# install git
apt install -y git &&\
# install kubectl
apt install -y apt-transport-https &&\
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - &&\
touch /etc/apt/sources.list.d/kubernetes.list &&\
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | tee -a /etc/apt/sources.list.d/kubernetes.list &&\
apt update &&\
apt install -y kubectl
