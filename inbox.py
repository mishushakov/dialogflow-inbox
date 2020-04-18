#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import smtplib
import imaplib
import requests
import logging

from dotenv import load_dotenv
from email import message_from_string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, make_msgid
from hashlib import md5
from langdetect import detect
from email_reply_parser import EmailReplyParser

# Retrieve environment variables
load_dotenv()
host = os.environ.get('INBOX_HOST')
user = os.environ.get('INBOX_USER')
password = os.environ.get('INBOX_PASSWORD')
fallback_lang = os.environ.get('FALLBACK_LANG')
catchall = os.environ.get('CATCHALL')
endpoint = os.environ.get('ENDPOINT')

# Connect to IMAP and fetch unread messages
server = imaplib.IMAP4_SSL(host)
server.login(user, password)
server.select('inbox')
mails, data = server.uid('search', None, 'UNSEEN')

for mail_id in data[0].split():
    # Fetch each unread E-Mail
    status, data = server.uid('fetch', mail_id, '(RFC822)')

    # Parse E-Mail
    parsed_email = message_from_string(data[0][1].decode('utf-8'))
    parsed_email_from = parseaddr(parsed_email['From'])[1]
    parsed_email_to = parseaddr(parsed_email['To'])[1]
    parsed_email_to_domain = parsed_email_to.split('@')[1]
    parsed_email_session = md5(bytes(parsed_email.get('Subject', '').replace('Re: ', '') + parsed_email_from, encoding='utf8')).hexdigest()
    parsed_email_body = ''
    for part in parsed_email.walk():
        if part.get_content_type() == 'text/plain':
            parsed_email_body += part.get_payload()

    parsed_email_body = EmailReplyParser.parse_reply(parsed_email_body)
    parsed_email_lang = fallback_lang
    try:
        parsed_email_lang = detect(parsed_email_body)
    except:
        pass

    # Log E-Mail
    logging.info('Received new E-Mail')
    logging.info('From: ' + parsed_email_from)
    logging.info('To: ' + parsed_email_to)
    logging.info('Text: ' + parsed_email_body)
    logging.info('Message ID: ' + parsed_email['Message-ID'])
    logging.info('Session ID: ' + parsed_email_session)

    # Build Request
    agent_id = parsed_email_to.split('@')[0]
    req = {
        'session': parsed_email_session,
        'queryInput': {
            'text': {
                'text': parsed_email_body,
                'languageCode': parsed_email_lang
            }
        },
        'queryParams': {
            'payload': {
                'email': {
                    'from': parsed_email_from,
                    'to': parsed_email_to,
                    'subject': parsed_email['Subject'],
                    'body': parsed_email_body
                }
            }
        }
    }

    # Make the request
    agent = requests.get(endpoint.replace('*', agent_id))
    r = requests.post(endpoint.replace('*', agent_id), json=req)
    if r.status_code == 200:
        # Make new E-Mail for the response
        message = MIMEMultipart()
        message['Message-ID'] = make_msgid()
        message['In-Reply-To'] = parsed_email['Message-ID']
        message['References'] = parsed_email['Message-ID']
        message['From'] = agent.json().get('displayName') + ' <' + parsed_email_to + '>' if agent.json().get('displayName') else parsed_email['To']
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

        # Send the E-Mail
        session = smtplib.SMTP(host, 587)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(user, password)
        session.sendmail(message['From'], message['To'], message.as_string())

        # Log response status
        app.logger.info('E-Mail response sent to ' + parsed_email_from)
    elif r.status_code == 404 and catchall:
         # Make new E-Mail for the response
        message = MIMEMultipart()
        message['Message-ID'] = make_msgid()
        message['In-Reply-To'] = parsed_email['Message-ID']
        message['Reply-To'] = parsed_email['From']
        message['References'] = parsed_email['Message-ID']
        message['From'] = 'no-reply@' + parsed_email_to_domain
        message['To'] = catchall
        message['Subject'] = parsed_email['Subject']
        message.attach(MIMEText(parsed_email_body, 'plain'))

        # Send the E-Mail
        session = smtplib.SMTP(host, 587)
        session.ehlo()
        session.starttls()
        session.ehlo()
        session.login(user, password)
        session.sendmail(message['From'], message['To'], message.as_string())

        # Log response status
        app.logger.info('E-Mail response sent to ' + parsed_email_from)
    else:
        # Log request error
        app.logger.error('Request failed')
        app.logger.error('Status: ' + str(r.status_code))
        app.logger.error(str(r.json()))

# Disconnect
server.close()
server.logout()