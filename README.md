# Dialogflow Inbox

![](https://i.imgur.com/8yoLPGI.png)

Dialogflow Inbox operates your Dialogflow Agent inside a mail server. It can automatically detect the languages and supports Webhooks (Dialogflow or Actions on Google)

This Integration is already included in [Dialogflow Gateway Hosted by Ushakov](https://dialogflow.cloud.ushakov.co) - Platform for building Dialogflow Integrations

## Getting Started

### Hosted Version

You may not need to host it by yourself, since [Dialogflow Gateway Hosted by Ushakov](https://dialogflow.cloud.ushakov.co) already ships with the Integration for free

Read [my medium article](https://medium.com/@ushakovhq/dialogflow-over-e-mail-85bd1b3dd8d6) to see how to enable it

### How it works

![](https://i.imgur.com/LliWtRV.png)

First we have the E-Mail client (which is installed on your machine), which you use to send E-Mails

Then, we have a Mailserver (SMTP, eg. Postfix), which we use as Ingress/Egress

Finally, we have a cronjob (`inbox.py`), which retrieves unread E-Mails from the IMAP-Server and forwards them to desired Dialogflow Agent to process and respond

### Drawbacks

- No HTML parsing
- No component rendering (only text is sent)

### Requirements

- Agent, that is connected to Dialogflow Gateway ([see a guide](https://github.com/mishushakov/dialogflow-gateway-docs/tree/master/hosted))
- SMTP and IMAP server of your choice. I prefer [docker-mailserver](https://github.com/tomav/docker-mailserver). You really don't want to mess with dockerizing 20yr old software on your own
- Domain and experience with editing DNS

### Setup

1. Install SMTP and IMAP Server on your machine and make sure it is working correctly
2. Create new user, which will recieve E-Mails for your agent
3. Assign alias: your-google-cloud-project-id@yourdomain.com or @yourdomain.com (if you have multiple Agents) to the user
4. Add MX record pointing to your machine

### Installation (Kubernetes)

1. Make sure your Mailserver is running
2. Create a CronJob with `dialogflow-inbox` container image:

```yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: dialogflow-inbox
spec:
  schedule: "* * * * *"
  successfulJobsHistoryLimit: 1
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: dialogflow-inbox
            image: docker.pkg.github.com/mishushakov/dialogflow-inbox/dialogflow-inbox:latest
            imagePullPolicy: IfNotPresent
            env:
              - name: INBOX_HOST
                value: <your-mailserver-host>
              - name: INBOX_USER
                value: <your-user>
              - name: INBOX_PASSWORD
                value: <your-user-password>
          restartPolicy: Never
```

Ps. obviously it's a good idea to save your environment in Secrets

3. Run `kubectl apply`

### Installation (manual)

If you want to install the code manually, follow the instructions:

1. Make sure your Mailserver is running
2. Clone the repository
3. Install Python and cron
4. Define the environment variables:
    - INBOX_USER=your-user
    - INBOX_PASSWORD=your-user-password
    - INBOX_HOST=your-mailserver-host
    - GATEWAY=https://cloud.ushakov.co
5. Send E-Mail to your Agent and run the `inbox.py` script with Python, to verify it works
6. Make a cronjob to run the script automatically

Done!