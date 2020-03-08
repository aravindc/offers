FROM python:3.7.4-alpine3.10
LABEL maintainer="aravindan.chockalingam@aimia.com"
ENV ADMIN="ara"

RUN apk update && apk upgrade && apk add bash

WORKDIR /usr/src/offers

COPY tescprod.py .

ENTRYPOINT ["python","./app/tescprod.py"]
