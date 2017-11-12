from django.core.mail import mail_admins


def send_email(subject, message):
    mail_admins(
        subject,
        message,
        # html_message=message,
    )