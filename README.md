# Dialogflow Inbox

![](https://i.imgur.com/8yoLPGI.png)

Dialogflow Inbox operates Dialogflow Agents inside a mail server

## Schema

![](https://i.imgur.com/LliWtRV.png)

## Features and Drawbacks

- Automatic language detection
- Reply recognition
- No HTML parsing
- No component rendering (only text is sent)

## Setup

1. Connect Agents to Dialogflow Gateway implementation ([more here](https://github.com/mishushakov/dialogflow-gateway-docs))
2. Install SMTP and IMAP server on your machine, i recommend [docker-mailserver](https://github.com/tomav/docker-mailserver)
3. Point DNS MX record to the SMTP and IMAP server
4. Create a user, which will recieve E-Mails for your agent
5. Assign alias: your-google-cloud-project-id@yourdomain.com or *@yourdomain.com (if you have multiple Agents) to the user

## Configuration

| Environment Variable | Description                       | Value                    |
|----------------------|-----------------------------------|--------------------------|
| INBOX_USER           | E-mail user                       | -                        |
| INBOX_PASSWORD       | E-mail user's password            | -                        |
| INBOX_HOST           | SMTP and IMAP server hostname     | -                        |
| GATEWAY              | Dialogflow Gateway Implementation | https://cloud.ushakov.co |

## Installation (Kubernetes)

See [k8s](k8s) directory

## Installation (manual)

1. Confirm your Mailserver is operating correctly
2. Clone the repository
3. Install Python and cron
4. Configure the environment variables
5. Send E-Mail to your Agent and run the [inbox.py](inbox.py) script with `python`
6. Setup a cronjob to run it automatically over a interval

Done!