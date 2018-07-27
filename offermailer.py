from smtplib import SMTP
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dbconfig import read_email_config


def send_email(toEmailId, emailSubject, emailMessage,
               files=None):
    params = read_email_config()
    fromId = params['smtp_user']
    smtpPass = params['smtp_pass']
    toId = toEmailId
    msg = MIMEMultipart()
    msg['From'] = fromId
    msg['To'] = toId
    msg['Subject'] = emailSubject
    message = emailMessage
    msg.attach(MIMEText(message))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=basename(f))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    with SMTP(params['smtp_host'], params['smtp_port'], timeout=60) as server:
        server.set_debuglevel(0)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(fromId, smtpPass)
        server.sendmail(fromId, toId, msg.as_string())
        server.quit()
