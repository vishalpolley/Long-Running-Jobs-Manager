FROM python:3.6-alpine

RUN apk update && \
    apk add redis

RUN pip3 install --upgrade pip setuptools httpie && \
    rm -r /root/.cache

WORKDIR /home/socialcops

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY main.py config.py boot.sh data.py run.py ./

RUN mkdir files
RUN mkdir files/datasets
RUN mkdir files/downloads
RUN mkdir files/uploads
RUN chmod +x boot.sh

ENV FLASK_APP main.py
ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
