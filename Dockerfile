FROM python:3.8-buster

RUN pip install -U pip pipenv
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --system --deploy

EXPOSE 8000
CMD gunicorn app:app -b 0.0.0.0:8000

COPY . /app
