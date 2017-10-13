from django.template import Context, TemplateDoesNotExist
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.conf import settings
import sys
import uuid


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
    # message = template.render(Context(ctx)) if template else ''
    message = template.render(dict(ctx)) if template else ''
    if template and message:
        return send_html_email(subject, message, receipient)
    return False


def unique_random_number(model):
    random_number = uuid.uuid4().hex[:12].upper()
    # print (' Model name: ', model.__name__, '-- random number', random_number)
    filter_result = model.objects.filter(account_no=random_number)
    if filter_result:
        unique_random_number(model)
    else:
        return random_number
