from celery import shared_task
from django.core.mail import send_mail

@shared_task
def verification_mail(username, first_name, last_name, email, code):
    subject = f'Verification for {username}'
    message = f'Dear {first_name} {last_name},\n\nHere is you verification code {code}'
    mail_sent = send_mail(subject,
                          message,
                          'admin@habrclone.com',
                          [email])
    return mail_sent