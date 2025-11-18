from django.db.models.signals import pre_save
from django.dispatch import receiver
from .views import send_mail, create_smtp_connection, base_context
from main.models import Guardian
import os
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator

def create_validation_link(user) -> str:
    token = default_token_generator.make_token(user)
    url = 'https://littleducklingschildminding.co.uk' if os.environ['DEBUG'] == 'False' else 'http://127.0.0.1'
    full_url = f'{url}/activate-account/{user.pk}/{token}/'
    return full_url

@receiver(pre_save, sender=Guardian)
def send_activation_link(sender, instance, **kwargs):
    if instance.pk is None:
        activation_link = create_validation_link(instance.user)
        message = f'''Thank you for signing up to {base_context["trading_name"]}! Please click on this link to activate your account:

    {activation_link}

    DO NOT share or forward this link to anybody, not even us. Doing so could compromise your account and your children\'s safety.'''
        try:
            with create_smtp_connection() as server:
                send_mail(
                    server=server,
                    subject='Account Activation Link',
                    plain_message=message,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[instance.user.email],
                )
        except Exception as e:
            print(e)
            messages.error('Something went wrong with sending the validation email. Please create the Guardian instance again.')
            raise ValidationError('Something went wrong with sending the validation email. Please create the Guardian instance again.')