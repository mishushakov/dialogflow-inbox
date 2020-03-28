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

### Preparation

1. Connect your Agents to a Dialogflow Gateway implementation ([more here](https://github.com/mishushakov/dialogflow-gateway-docs))
2. Install SMTP and IMAP server on your machine, i recommend [docker-mailserver](https://github.com/tomav/docker-mailserver)
3. Point DNS MX record to the SMTP and IMAP server
4. Create a user, which will recieve E-Mails for your agent
5. Assign alias: your-google-cloud-project-id@yourdomain or *@yourdomain (if you have multiple Agents) to the user

### Installation

#### Kubernetes

See [k8s](k8s) for examples

#### Manual

1. Confirm your Mailserver operates correctly
2. Clone the repository
3. Install Python and cron
4. Install the requirements with `pip install -r requirements.txt`
5. Configure the environment variables (below)
6. Send a test E-Mail to your-google-cloud-project-id@yourdomain and run the [inbox.py](inbox.py) script with `python`
7. Setup a cronjob to run it automatically over a interval

### Configuration

| Environment Variable | Description                                                   | Value                        |
|----------------------|---------------------------------------------------------------|------------------------------|
| INBOX_USER           | E-mail user                                                   | -                            |
| INBOX_PASSWORD       | E-mail user's password                                        | -                            |
| INBOX_HOST           | SMTP and IMAP server hostname                                 | -                            |
| FALLBACK_LANG        | Fallback language if language detection fails                 | en                           |
| ENDPOINT             | Dialogflow Gateway Endpoint. `*` for wildcard                 | https://*.core.ushaflow.io   |
| DEBUG                | Debug mode                                                    | true                         |
| PORT                 | Listen on port                                                | 5000                         |