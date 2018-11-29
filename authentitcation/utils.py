from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.conf import settings

def send_registration_email(user):
    subject = "Registration at website"
    to = [user.email]
    from_email = settings.EMAIL_HOST_USER

    ctx = {
        'user': user,
        'settings': settings
    }

    message = render_to_string('email/registration.html', ctx)

    EmailMessage(subject, message, to=to, from_email=from_email).send()

    return True