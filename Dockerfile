FROM python:3.9-buster

RUN apt update && pip3 install poetry && mkdir /opt/app

COPY poetry.lock /opt/app
COPY pyproject.toml /opt/app

WORKDIR /opt/app

RUN poetry install

COPY ./ /opt/app

ENV FLASK_APP="checklens:create_app"

EXPOSE 5000

CMD poetry run flask run -h 0.0.0.0