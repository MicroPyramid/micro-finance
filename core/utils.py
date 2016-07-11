from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.conf import settings
import sys


def send_html_email(subject, message, receipient):
    # Send an Email
    msg = EmailMessage(subject, message, settings.FROM_EMAIL, [receipient])
    msg.content_subtype = "html"
    response = msg.send()
    return response


def send_email_template(subject, template_name, ctx, receipient):
    if 'test' in sys.argv:
        return True
    try:
        template = get_template(template_name)
    except TemplateDoesNotExist:
        template = None
    message = template.render(Context(ctx)) if template else ''
    if template and message:
        return send_html_email(subject, message, receipient)
    return False
