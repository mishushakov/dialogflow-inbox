FROM python:alpine

ADD inbox.py .
ADD requirements.txt .

ENV FALLBACK_LANG en
ENV ENDPOINT https://{}.core.ushaflow.com

RUN pip install -r requirements.txt

ENTRYPOINT python inbox.py