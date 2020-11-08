FROM python:3.7

WORKDIR /app


COPY . .

RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get -y install apt-utils gcc libpq-dev libsndfile-dev

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD [ "uwsgi", "./app.ini" ]

