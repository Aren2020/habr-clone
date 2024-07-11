from celery import shared_task
from django.core.mail import send_mail

@shared_task
def verification_mail(username, full_name, email, code):
    subject = f'Verification for {username}'
    message = f'Dear {full_name},\n\nHere is you verification code {code}'
    mail_sent = send_mail(subject,
                          message,
                          'admin@habrclone.com',
                          [email])
    return mail_sent

@shared_task
def password_reset_mail(username, full_name, email, reset_url):
    subject = f'Verification for {username}'
    message = f'Dear {full_name},\n\nHere is you reset password url {reset_url}'
    mail_sent = send_mail(subject,
                          message,
                          'admin@habrclone.com',
                          [email])
    return mail_sent