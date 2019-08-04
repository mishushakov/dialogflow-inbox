#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import smtplib
import imaplib
import email
import requests
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr
from langdetect import detect

# Retrieve environment variables
username = os.environ['INBOX_USER']
password = os.environ['INBOX_PASSWORD']
host = os.environ['INBOX_HOST']
gateway = os.environ['GATEWAY']

# Connect to IMAP and fetch unread messages
server = imaplib.IMAP4_SSL(host)
server.login(username, password)
server.select('inbox')
mails, data = server.uid('search', None, 'UNSEEN')

# Enable Debugging
logging.getLogger().setLevel(logging.DEBUG)

for mail_id in data[0].split():
    # Fetch each unread E-Mail
    status, data = server.uid('fetch', mail_id, '(RFC822)')
    raw_email = data[0][1].decode('utf-8')

    # Parse E-Mail
    parsed_email = email.message_from_string(raw_email)
    parsed_email_from = parseaddr(parsed_email['From'])[1]
    parsed_email_to = parseaddr(parsed_email['To'])[1]
    parsed_email_body = ''
    for part in parsed_email.walk():
        if part.get_content_type() == 'text/plain':
            parsed_email_body += part.get_payload()

    # Log E-Mail
    logging.info('Recieved new E-Mail')
    logging.info('From: ' + parsed_email_from)
    logging.info('To: ' + parsed_email_to)
    logging.info('Subject: ' + parsed_email['Subject'])
    logging.info('Text: ' + parsed_email_body)

    # Build Dialogflow Gateway Request
    agent_id = parsed_email_to.split('@')[0]
    req = {
        'session': parsed_email_from,
        'queryInput': {
            'text': {
                'text': parsed_email_body,
                'languageCode': detect(parsed_email_body)
            }
        }
    }

    # Make the request
    baseurl = agent_id + '.gateway.dialogflow.cloud.ushakov.co'
    agent = requests.get(gateway, headers={'Host': baseurl})
    r = requests.post(gateway, headers={'Host': baseurl}, json=req)
    if r.status_code == 200:
        # Make new E-Mail for the response
        message = MIMEMultipart()
        message['Message-ID'] = email.utils.make_msgid()
        message['In-Reply-To'] = parsed_email['Message-ID']
        message['References'] = parsed_email['Message-ID']
        message['From'] = (agent.json()['displayName'] + ' <' + parsed_email_to + '>') or parsed_email['To']
        message['To'] = parsed_email['From']
        message['Subject'] = parsed_email['Subject']

        # Attach the components
        result = r.json()['queryResult']
        if 'fulfillmentMessages' in result:
            for component in result['fulfillmentMessages']:
                if 'text' in component:
                    message.attach(MIMEText(component['text']['text'][0], 'plain'))
                elif 'simpleResponses' in component:
                    message.attach(MIMEText(component['simpleResponses']['simpleResponses'][0]['textToSpeech'], 'plain'))

        if 'webhookPayload' in result:
            if 'google' in result['webhookPayload']:
                for component in result['webhookPayload']['google']['richResponse']['items']:
                    if 'simpleResponse' in component:
                        message.attach(MIMEText(component['simpleResponse']['textToSpeech'], 'plain'))

        message.attach(MIMEText('<br><br>Powered by <a href="https://dialogflow.cloud.ushakov.co">Dialogflow Gateway</a>', 'html'))

        # Connect to SMTP and send the E-Mail
        session = smtplib.SMTP(host, 587)
        session.ehlo()
        session.starttls()
        session.ehlo()

        session.login(username, password)
        session.sendmail(parsed_email['To'], parsed_email['From'], message.as_string())

        # Log response status
        logging.info('E-Mail response sent to ' + parsed_email_from)
    else:
        # Log request error
        logging.error('Dialogflow Gateway request failed')
        logging.error('Status: ' + r.status_code)
        logging.error('Error: ' + r.json())

# Disconnect
server.close()
server.logout()