import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse


base_context = {
    'trading_name': 'Little Ducklings Childminding',
    'price_gbp': 45,
    'location_name': 'Baddeley Green, Stoke-on-Trent',
}


def inject_context(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        kwargs['context'] = dict(base_context)
        kwargs['context']['site_url'] = request.build_absolute_uri('/').rstrip('/')
        kwargs['context']['full_url'] = kwargs['context']['site_url']
        kwargs['context']['canonical_url'] = request.build_absolute_uri(request.path)
        return view_func(request, *args, **kwargs)

    return wrapper


def create_smtp_connection(
    email=os.getenv('EMAIL_ADDRESS'),
    password=os.getenv('EMAIL_PASSWORD'),
    smtp_host=os.getenv('SMTP_HOST'),
    smtp_port=int(os.getenv('SMTP_PORT', 465)),
):
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=context)
    server.login(email, password)
    return server


def send_mail(server, subject, plain_message, from_email, to_emails, reply_to=None, from_name='Little Ducklings Childminding'):
    for recipient in to_emails:
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f'"{from_name}" <{from_email}>'
        message['To'] = recipient
        if reply_to:
            message['Reply-To'] = reply_to
        message.attach(MIMEText(plain_message, 'plain'))
        server.sendmail(from_email, recipient, message.as_string())


def robots_txt(request: HttpRequest):
    content = render_to_string(
        'robots.txt',
        {'sitemap_url': f'{settings.SITE_URL}{reverse("sitemap")}'},
    )
    return HttpResponse(content, content_type='text/plain')


@inject_context
def home(request: HttpRequest, context=None):
    if request.method == 'POST':
        name = request.POST['nombre']
        email = request.POST['email']
        tel = request.POST['tel']
        msg = request.POST['msg']
        mensaje = request.POST['mensaje']
        letter = request.POST['letter']
        phone = request.POST['phone']
        telefono = request.POST['telefono']

        validation_list = [
            mensaje == msg,
            telefono == 'Go away naughty bots',
            letter == '62668977',
            phone == '82636683',
        ]
        if False in validation_list:
            return redirect('/?naughty_bot=True')

        full_message = f'''This message was submitted via {context["full_url"]}.

From: {name}
Email: {email}
Telephone: {tel}

Message:

{msg}'''
        try:
            with create_smtp_connection() as server:
                send_mail(
                    server=server,
                    subject=f'{name} sent you a message on {context["trading_name"]}',
                    plain_message=full_message,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=['lauraanneoldfield@outlook.com'],
                    reply_to=f'"{name}" <{email}>',
                    from_name=name,
                )
            context['message_success'] = True
        except (OSError, smtplib.SMTPException):
            context['message_error'] = True

    return render(request, 'home.html', context)


@inject_context
def gallery(request: HttpRequest, context=None):
    return render(request, 'gallery.html', context)


@inject_context
def policy_menu(request: HttpRequest, context=None):
    return render(request, 'policy_menu.html', context)


@inject_context
def get_policy(request: HttpRequest, policy_slug, context=None):
    try:
        return render(request, f'policies/{policy_slug}.html', context)
    except TemplateDoesNotExist:
        raise Http404('Policy not found')
