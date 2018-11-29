from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags

def send_registration_email(user):
    subject = "Registration at website"
    to = [user.email]
    from_email = settings.EMAIL_HOST_USER

    ctx = {
        'user': user,
        'settings': settings
    }

    html_content = render_to_string('email/registration.html', ctx)
    text_content = strip_tags(html_content) 

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return True