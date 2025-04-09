import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def send_email_notification(
    status: str,
    postgres_host: str,
    directories: list,
    version: str,
    change_log_file: str,
    failed_changeset: str,
    caused_by: str,
    traceback_str: str
):
    subject = f"[{status}] Schema Deployment - Tag {version}"
    
    body = f"""
    <html>
    <body>
    <p><strong>Status:</strong> {status}</p>
    <p><strong>Postgres Host:</strong> {postgres_host}</p>
    <p><strong>Schema Directories:</strong> {', '.join(directories)}</p>
    <p><strong>Tag:</strong> {version}</p>
    <p><strong>ChangeLog File:</strong> {change_log_file}</p>
    <p><strong>Failed Changeset:</strong> {failed_changeset}</p>
    <p><strong>Error Log:</strong><br><pre>{caused_by}</pre></p>
    <p><strong>Traceback:</strong><br><pre>{traceback_str}</pre></p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = config.EMAIL_USER
    msg['To'] = ", ".join(config.EMAIL_RECIPIENTS)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
            server.starttls()
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_USER, config.EMAIL_RECIPIENTS, msg.as_string())
        print("----------> Email notification sent successfully.")
    except Exception as e:
        print("----------> Failed to send email notification.")
        print(str(e))
