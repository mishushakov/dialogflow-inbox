# Dialogflow Inbox

![](https://i.imgur.com/8yoLPGI.png)

Dialogflow Inbox operates a Dialogflow Agent inside a mail server. It automatically detects language and e-mail reply and supports Webhooks (Dialogflow or Actions on Google)

## Getting Started

### Infrastructure

![](https://i.imgur.com/LliWtRV.png)

E-Mail client, used to send E-Mails

A Mailserver (SMTP, eg. Postfix), used as Ingress/Egress

A cronjob ([inbox.py](inbox.py)), fetches unread E-Mails from the IMAP server and forwards them to desired Dialogflow Agent to process and respond

### Drawbacks

- No HTML parsing
- No component rendering (only text is sent)

### Requirements

- Agent, that is connected to Dialogflow Gateway ([see a guide](https://github.com/mishushakov/dialogflow-gateway-docs))
- SMTP and IMAP server of your choice. I prefer [docker-mailserver](https://github.com/tomav/docker-mailserver). You really don't want to mess with dockerizing 20yr old software on your own
- Domain and experience with editing DNS

### Setup

1. Install SMTP and IMAP server on your machine. Make sure it is working correctly
2. Create new user, which will recieve E-Mails for your agent
3. Assign alias: your-google-cloud-project-id@yourdomain.com or @yourdomain.com (if you have multiple Agents) to the user
4. Add MX record pointing to the machine

### Installation (Kubernetes)

See [k8s](k8s) directory

### Installation (manual)

1. Confirm, that your Mailserver is operating correctly
2. Clone the repository
3. Install Python and cron
4. Set the environment variables:
    - INBOX_USER=your-user
    - INBOX_PASSWORD=your-user-password
    - INBOX_HOST=your-mailserver-host
    - GATEWAY=https://cloud.ushakov.co
5. Send E-Mail to your Agent and run the [inbox.py](inbox.py) script with Python
6. Setup a cronjob to run the script automatically

Done!