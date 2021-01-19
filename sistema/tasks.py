from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task
def add():
    subject, from_email, to = 'hello', 'plainced@gmail.com', 'jafetandres@hotmail.com'
    text_content = 'This is an important message.'
    html_content = '<p>This is an <strong>important</strong> message.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
