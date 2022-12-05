from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from accounts.constants import *


def send_user_email(request,user_name,template_name,mail_subject,to_email):
    current_site = get_current_site(request)
    context = {
        'domain':current_site.domain,
        'site_name': current_site.name,
        'protocol': 'https' if USE_HTTPS else 'http',
        'name': user_name,
    }
    message = render_to_string(str(template_name), context)        
    email_message = EmailMultiAlternatives(mail_subject, message, settings.EMAIL_HOST_USER, [to_email])
    html_email = render_to_string(str(template_name),context)
    email_message.attach_alternative(html_email, 'text/html')
    email_message.send()