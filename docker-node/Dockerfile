FROM node

WORKDIR /srv
COPY app.js /srv
COPY public/index.html /srv/public/index.html

# generate ssl certificate
RUN openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CA/ST=QC/L=Montreal/O=None/OU=None/CN=None"
