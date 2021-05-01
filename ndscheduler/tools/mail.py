"""Functions to send an email"""

from ndscheduler import settings

import smtplib
import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename


def send(
    mail_from: str, mail_to: list, subject: str, text: str, priority=3, attachments=[],
) -> dict:
    """Send email

    Parameters
    ----------
    mail_from : str
        Sender email address
    mail_to : list(string)
        List of recipients
    subject : str
        Email subject line
    test : str
        Email body text
    priority : int, optional
        Email priority (1 = high, 5 = low)
    attachments : list(str)
        List of file names to be attached.
    Returns
    -------
    dict
        "returncode" : int
            Value of the script exit code (0 = success)
    """

    logger = logging.getLogger()

    msg = MIMEMultipart()
    msg["From"] = mail_from
    msg["To"] = COMMASPACE.join(mail_to)
    recipients = mail_to.copy()
    # if copy_to:
    #     msg["Cc"] = COMMASPACE.join(copy_to)
    #     recipients += copy_to
    msg["Date"] = formatdate(localtime=True)
    msg["Subject"] = subject
    msg["X-Priority"] = str(priority)
    # recipients += "test"
    msg.attach(MIMEText(text))

    # Add attachments
    for file in attachments:
        if file is not None:
            try:
                with open(file, "rb") as f:
                    part = MIMEApplication(f.read(), Name=basename(file))
                # After the file is closed
                part["Content-Disposition"] = 'attachment; filename="%s"' % basename(
                    file
                )
                msg.attach(part)
            except FileNotFoundError:
                logger.debug(
                    f"Failed to send mail from {mail_from} to {recipients}, file '{file}' doesn't exist"
                )
                return {"returncode": 10, "error": f"File '{file}' doesn't exist"}
            except PermissionError:
                logger.debug(
                    f"Failed to send mail from {mail_from} to {recipients}, file '{file}' access denied"
                )
                return {"returncode": 11, "error": f"Access denied for file '{file}'"}

    result = 0
    error_msg = ""
    for smtp_server in settings.MAIL_SERVER:
        try:
            smtp = smtplib.SMTP(smtp_server)
            smtp.sendmail(mail_from, recipients, msg.as_string())
            smtp.close()
            break
        except ConnectionRefusedError:
            error_msg = f"Server {smtp_server}: Connection refused."
            result = 1
        except smtplib.SMTPRecipientsRefused:
            error_msg = f"Server {smtp_server}: Recipient refused to: {mail_to}"
            result = 2
        except smtplib.SMTPSenderRefused:
            error_msg = f"Server {smtp_server}: Sender refused: {mail_from}"
            result = 3
        except smtplib.SMTPException as e:
            error_msg = f"Server {smtp_server}: {e}"
            result = 4

    logger.debug(
        f"Mail sent from {mail_from} to {recipients}, result={result}, error='{error_msg}'"
    )
    return {"returncode": result, "error": error_msg}
