FROM python:alpine

ENV INBOX_USER=inbox
ENV INBOX_PASSWORD=123454321
ENV INBOX_HOST=0.0.0.0
ENV GATEWAY=https://cloud.ushakov.co

ADD inbox.py .
ADD requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT python inbox.py