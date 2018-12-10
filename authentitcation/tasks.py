# main/tasks.py
 
import logging
logger = logging.getLogger('admin_log')

from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags


from imgdownloader.celery import app
from .models import User

@app.task
def send_registration_email(user_id):
    user = User.objects.get(id=user_id)
    subject = "Registration at website"
    to = [user.email]
    from_email = settings.EMAIL_HOST_USER

    ctx = {
        'user': user,
        'settings': settings
    }

    html_content = render_to_string('email/registration.html', ctx)
    text_content = strip_tags(html_content) 
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as e:
        logging.warning("Tried to send verification email to non-existing user '%s'" % user.id)
    return True