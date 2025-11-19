from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest
from django.template import TemplateDoesNotExist
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from main.sanitisers import *
from main.models import Guardian, ChildmindingContract, ConsentForm, ChildRecord, Child, DailyRegister
#Email Imports
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from functools import wraps
from weasyprint import HTML

base_context = {
    'trading_name': 'Little Ducklings Childminding',
    'price_gbp': 45,
}

# Wrappers

def inject_context(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        kwargs['context'] = dict(base_context)
        kwargs['context']['full_url'] = request.build_absolute_uri('/').rstrip('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def requires_guardian(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            guardian = Guardian.objects.filter(user=request.user)
            if guardian.exists():
                kwargs['guardian'] = guardian[0]
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have a Guardian instance attached to your user. Please contact us to resolve the issue.')
                return redirect('home')
        else:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login')
    return wrapper

def requires_guardians_child(view_func):
    @wraps(view_func)
    def wrapper(request, child_pk, *args, **kwargs):
        child = kwargs['guardian'].child_set.filter(pk=child_pk)
        if child.exists():
            child = child[0]
            kwargs['child'] = child
        else:
            messages.error(request, 'The requested child either does not exist, or you do not have permission to access.')
            return redirect('parent_dashboard')
        return view_func(request, child_pk, *args, **kwargs)
    return wrapper


# Useful Functions

def create_validation_link(request:HttpRequest, user:User, for_view:str) -> str:
    token = default_token_generator.make_token(user)
    path = reverse(for_view, args=[user.pk, token])
    full_url = request.build_absolute_uri(path)
    return full_url

def create_smtp_connection(
        email=os.getenv('EMAIL_ADDRESS', None),
        password=os.getenv('EMAIL_PASSWORD', None),
        smpt_host=os.getenv('SMTP_HOST', None),
        smtp_port=int(os.getenv('SMTP_PORT', 465))
        ):
    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(smpt_host, smtp_port, context=context)
        server.login(email, password)
        return server
    except Exception as e:
        print(f"Error Connecting to SSL Server: {e}")
        return None

def send_mail(server, subject, plain_message, from_email, to_emails, reply_to=None, html_message=None, from_name='Little Ducklings Childminding', attachments=[]):
    for i in to_emails:
        message = MIMEMultipart("alternative")
        message['Subject'] = subject
        message['From'] = f'"{from_name}" <{from_email}>'
        message['To'] = i
        if reply_to:
            message['Reply-To'] = reply_to
        part1 = MIMEText(plain_message, 'plain')
        message.attach(part1)
        if html_message is not None:
            part2 = MIMEText(html_message, 'html')
            message.attach(part2)
        for j in attachments:
            mime_base = MIMEBase('application', 'octet-stream')
            mime_base.set_payload(j[0])
            encoders.encode_base64(mime_base)
            mime_base.add_header('Content-Disposition', f'attachment; filename="{j[1]}"')
            message.attach(mime_base)
        try:
            server.sendmail(from_email, i, message.as_string())
        except Exception as e:
            print(f'Error Sending Mail to {i}: {e}')

def contract_pdf(contract):
    html_string = render_to_string('html_to_pdf/contract.html', {'contract': contract})
    pdf_file = HTML(string=html_string).write_pdf()
    return pdf_file

def consent_pdf(consent):
    html_string = render_to_string('html_to_pdf/consent.html', {'consent': consent})
    pdf_file = HTML(string=html_string).write_pdf()
    return pdf_file

def child_record_pdf(record):
    html_string = render_to_string('html_to_pdf/child_record.html', {'record': record, 'trading_name': base_context['trading_name']})
    pdf_file = HTML(string=html_string).write_pdf()
    return pdf_file

# Create your views here.

@inject_context
def home(request:HttpRequest, context=None):
    if request.method == 'POST':
        name = request.POST['nombre']
        email = request.POST['email']
        tel = request.POST['tel']
        msg = request.POST['msg']
        mensaje = request.POST['mensaje']
        letter = request.POST['letter']
        phone = request.POST['phone']
        mobile = request.POST['mobile']
        telefono = request.POST['telefono']
        reply_to = f'"{name}" <{email}>'

        validation_list = [
            mensaje == msg,
            telefono == 'Go away naughty bots',
            letter == '62668977',
            phone == '82636683',
        ]
        if False in validation_list:
            return redirect('/?naughty_bot=True')
        
        subject = f'{name} sent you a message on {context["trading_name"]}'
        full_message = f'''This message was submitted via {context["full_url"]}.

From: {name}
Email: {email}
Telephone: {tel}

Message:

{msg}'''
        with create_smtp_connection() as server:
            send_mail(
                server=server,
                subject=subject,
                plain_message=full_message,
                from_email=os.environ['EMAIL_ADDRESS'],
                to_emails=[
                    'lauraanneoldfield@outlook.com',
                ],
                reply_to=reply_to,
                from_name=name,
            )
            context['message_success'] = True
    return render(request, 'home.html', context)

@inject_context
def gallery(request:HttpRequest, context=None):
    return render(request, 'gallery.html', context)

@inject_context
def policy_menu(request:HttpRequest, context=None):
    return render(request, 'policy_menu.html', context)

@inject_context
def get_policy(request:HttpRequest, policy_slug, context=None):
    try:
        return render(request, f'policies/{policy_slug}.html', context)
    except TemplateDoesNotExist:
        raise Http404('Policy not found')

@inject_context
def login_view(request:HttpRequest, context=None):
    if request.user.is_authenticated:
        messages.error(request, 'Logged in users cannot access the login page. Please log out and try again.')
        return redirect('home')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        validation_list = [
            request.POST['b'] == 'spongealarm',
            request.POST['d'] == 'chairshed',
            request.POST['a'] == password,
            request.POST['c'] == email,
        ]
        if False not in validation_list:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login Successful')
                if request.user.is_staff:
                    return redirect('staff_dashboard')
                return redirect('parent_dashboard')
            else:
                messages.error(request, 'Email and password are not a valid combination, please try again.\\n\\nIf you have forgotten your password, please tap the "Forgot Your Password?" link below.')
        else:
            messages.error(request, 'The form data was corrupted. If you are using autofill, please try again and manually input your information.')
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

@inject_context
def password_reset_view(request, context=None):
    if request.user.is_authenticated:
        messages.error(request, 'Logged in users cannot access the password reset page. Please log out and try again.')
        return redirect('home')
    if request.method == 'POST':
        email = clean_email(request.POST['email'])
        validation_list = [
            request.POST['a'] == 'fanwheel',
            request.POST['b'] == email,
        ]
        if False in validation_list:
            messages.error(request, 'The form data was corrupted. If you are using autofill, please try again and manually input your information.')
            return redirect('home')
        user = User.objects.filter(username=email)
        if user.exists():
            user = user[0]
            reset_link = create_validation_link(request, user, 'password_verify')
            try:
                message = f'''Hello {user.first_name},

Please reset your password by clicking the below link:

{reset_link}

DO NOT share or forward this link to anybody, not even us. Doing so could compromise your account and your children\'s safety.'''
                with create_smtp_connection() as server:
                    send_mail(
                        server=server,
                        subject='Password Reset Link',
                        plain_message=message,
                        from_email=os.environ['EMAIL_ADDRESS'],
                        to_emails=[email],
                    )
            except Exception as e:
                messages.error(request, 'Something went wrong with sending the email. Please try again.')
                print(e)
                return redirect('password_reset')
        messages.success(request, 'If an account with this email exists, you will have received a reset link via your email inbox to reset your password.')
        return redirect('login')
    return render(request, 'forgot_password/reset.html', context)

@inject_context
def password_verify_view(request, uid, token, context=None):
    if request.user.is_authenticated:
        messages.error(request, 'Logged in users cannot access the password verification page. Please log out and try again.')
        return redirect('home')
    user = User.objects.filter(pk=uid)
    if user.exists():
        user = user[0]
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                password = request.POST['password']
                validation_list = [
                    user.username == request.POST['email'],
                    user.username == request.POST['b'],
                    request.POST['a'] == 'monsterbiscuit',
                    validate_passwords(password, request.POST['confirm_password']),
                ]
                if False in validation_list:
                    messages.error(request, 'The form data was corrupted. If you are using autofill, please try again and manually input your information.')
                    return redirect('home')
                else:
                    user.set_password(password)
                    user.is_active = True
                    user.save()
                    messages.success(request, 'Your password has now been reset. You can now log in with your new password.')
                    return redirect('login')
            else:
                context.update(uid=uid, token=token, user_email=user.username)
                return render(request, 'forgot_password/change.html', context)
    messages.error(request, 'Sorry, this link is not valid.')
    return redirect('home')

def activate_account_view(request, uid, token):
    if request.user.is_authenticated:
        messages.error(request, 'Logged in users cannot activate new accounts. Please log out and try again.')
        return redirect('home')
    user = User.objects.get(pk=uid)
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        guardian = Guardian.objects.get(user=user)
        guardian.ipv4_on_activation = request.headers['X-Real-IP']
        guardian.time_on_activation = timezone.now()
        guardian.save()
        messages.success(request, f'Hello {user.first_name}! Your account has succesfully been activated. You can now login!')
        return redirect('login')
    else:
        messages.error(request, 'Sorry, this link is not valid.')
        return redirect('home')
    
@inject_context
@requires_guardian
def parent_dashboard_view(request, context=None, guardian=None):
    context['children'] = guardian.child_set.all()
    return render(request, 'parent_dashboard.html', context)

@inject_context
@staff_member_required
def staff_dashboard_view(request, context=None):
    return render(request, 'staff_dashboard.html', context)
    
@inject_context
@requires_guardian
@requires_guardians_child
def child_view(request, child_pk, context=None, guardian=None, child=None):
    context['child'] = child
    context['contract'] = getattr(child, "contract", None)
    context['consent'] = getattr(child, "consent", None)
    context['record'] = getattr(child, "record", None)
    return render(request, 'child.html', context)

@inject_context
@staff_member_required
def child_register_view(request, context=None):
    context['children'] = Child.objects.all()
    return render(request, 'child_register.html', context)


@staff_member_required
def clock_in_child(request, child_pk):
    if request.method == 'POST':
        child = Child.objects.get(pk=child_pk)
        reg_check = DailyRegister.objects.filter(
            child=child,
            clock_out=None,
        )
        if reg_check.exists():
            messages.error(request, 'You must clock out this child from an existing clock punch before you can clock them in again')
        else:
            DailyRegister.objects.create(
                child=child,
            )
            messages.success(request, 'Child has been successfully clocked in')
    else:
        messages.error(request, f'{request.method} request method not supported for this URL')
    return redirect('child_register')

@staff_member_required
def clock_out_child(request, child_pk):
    if request.method == 'POST':
        child = Child.objects.get(pk=child_pk)
        reg_check = DailyRegister.objects.filter(
            child=child,
            clock_out=None,
        )
        if reg_check.exists():
            reg = reg_check[0]
            reg.clock_out = timezone.now()
            reg.save()
            messages.success(request, 'Child has been successfully clocked out')
        else:
            messages.error(request, 'Child must be clocked in before being able to clock out')
    else:
        messages.error(request, f'{request.method} request method not supported for this URL')
    return redirect('child_register')

# Contract Views
    
@inject_context
@requires_guardian
@requires_guardians_child
def child_contract_view(request, child_pk, context=None, guardian=None, child=None):
    context['child'] = child
    # Check if child has contract in place already 
    contract = getattr(child, "contract", None)
    if contract is None:
        return render(request, 'child_forms/contract.html', context)
    else:
        messages.error(request, f'Contract is already in place for {child.first_name} {child.last_name}.')
        return redirect('parent_dashboard')
    
@inject_context
@requires_guardian
@requires_guardians_child
def save_contract_view(request, child_pk, context=None, guardian=None, child=None):
    if request.method == 'POST':
        contract = getattr(child, "contract", None)
        if contract:
            messages.error(request, f'Cannot submit another contract as {child.first_name} {child.last_name} already has one in place.')
            return redirect('child', child.pk)
        else:
            data = request.POST
            contract = ChildmindingContract.objects.create(
                child=child,
                parent1_name=trim_name(data['parent1_name']),
                parent1_address=trim_whitespace(data['parent1_address']),
                parent1_telephone_home=clean_phone(data['parent1_telephone_home']) if data['parent1_telephone_home'] else None,
                parent1_telephone_work=clean_phone(data['parent1_telephone_work']) if data['parent1_telephone_work'] else None,
                parent1_telephone_mobile=clean_phone(data['parent1_telephone_mobile']) if data['parent1_telephone_mobile'] else None,
                parent2_name=trim_name(data['parent2_name']) if data['parent2_name'] else None,
                parent2_address=trim_whitespace(data['parent2_address']) if data['parent2_address'] else None,
                parent2_telephone_home=clean_phone(data['parent2_telephone_home']) if data['parent2_telephone_home'] else None,
                parent2_telephone_work=clean_phone(data['parent2_telephone_work']) if data['parent2_telephone_work'] else None,
                parent2_telephone_mobile=clean_phone(data['parent2_telephone_mobile']) if data['parent2_telephone_mobile'] else None,
                legal_contact=trim_whitespace(data['legal_contact']) if data['legal_contact'] else None,
                authorised_collectors=trim_whitespace(data['authorised_collectors']) if data['authorised_collectors'] else None,
                collection_password=trim_whitespace(data['collection_password']),
                day_fee_gbp=context['price_gbp'],
                start_date=child.contract_start_date,
                parent_signature=data['parent_signature'],
                parent_ip=request.headers['X-Real-IP'],
            )
            subject = f'Contract signed for {child.first_name} {child.last_name}'
            message_parent = f'Hello {guardian.user.first_name},\n\nThank you so much for completing your child\'s contract. We cannot wait to welcome {child.first_name} to our setting!\n\nPlease see attached your filled-out contract. If you have any issues with the contents of the contract, or if this wasn\'t you filling out the contract, please contact us immediately.\n\nKind regards,\n\n{context["trading_name"]}'
            message_childminder = f'{guardian.user.first_name} {guardian.user.last_name} has signed a contract on behalf of their child, {child.first_name} {child.last_name}.'
            attachment = contract_pdf(contract)
            email_attachments = [
                [attachment, f'{child.first_name}_{child.last_name}_Contract.pdf'],
            ]
            with create_smtp_connection() as server:
                send_mail(
                    server=server,
                    subject=subject,
                    plain_message=message_childminder,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[os.environ['EMAIL_ADDRESS']],
                    reply_to=f'"{guardian.user.first_name} {guardian.user.last_name}" <{guardian.user.email}>',
                    attachments=email_attachments
                )
                send_mail(
                    server=server,
                    subject=subject,
                    plain_message=message_parent,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[guardian.user.email],
                    reply_to=f'\"{context["trading_name"]}\" <{os.environ["EMAIL_ADDRESS"]}>',
                    attachments=email_attachments
                )
            messages.success(request, f'Thank you for completing {child.first_name} {child.last_name}\\\'s contract. {context["trading_name"]} will review it shortly and be in touch.')
            return redirect('child', child.pk)
    else:
        messages.error(request, f'You cannot access this page via a {request.method} request.')
        return redirect('child', child.pk)
    
# Consent Views

@inject_context
@requires_guardian
@requires_guardians_child
def child_consent_view(request, child_pk, context=None, guardian=None, child=None):
    context['child'] = child
    # Check if child has consent in place already 
    consent = getattr(child, "consent", None)
    if consent is None:
        return render(request, 'child_forms/consent.html', context)
    else:
        messages.error(request, f'Consent form is already in place for {child.first_name} {child.last_name}.')
        return redirect('parent_dashboard')


@inject_context
@requires_guardian
@requires_guardians_child
def save_consent_view(request, child_pk, context=None, guardian=None, child=None):
    if request.method == 'POST':
        consent = getattr(child, "consent", None)
        if consent:
            messages.error(request, f'Cannot submit another consent form as {child.first_name} {child.last_name} already has one in place.')
            return redirect('child', child.pk)
        else:
            data = request.POST
            consent = ConsentForm.objects.create(
                child=child,
                policies_signature=data['policies_signature'],
                complaints_signature=data['complaints_signature'],
                emergency_signature=data['emergency_signature'],
                emergency_caregiver_signature=data['emergency_caregiver_signature'],
                outings_signature=data['outings_signature'],
                photos_signature=data['photos_signature'],
                transport_signature=data['transport_signature'],
                equipment_signature=data['equipment_signature'],
                firstaid_signature=data['firstaid_signature'],
                sharing_signature=data['sharing_signature'],
                plaster_signature = data['plaster_signature'],
                suncream_wipes_signature=data['suncream_wipes_signature'],
                calpol_signature=data['calpol_signature'],
                parent_signature=data['parent_signature'],
                parent_ip=request.headers['X-Real-IP'],
            )

            subject = f'Consent form signed for {child.first_name} {child.last_name}'
            message_parent = f'Hello {guardian.user.first_name},\n\nThank you for completing your child\'s consent forms. We cannot wait to welcome {child.first_name} to our setting!\n\nPlease see attached your filled-out consent form. If you have any issues with the contents of the form, or if this wasn\'t you filling it out, please contact us immediately.\n\nKind regards,\n\n{context["trading_name"]}'
            message_childminder = f'{guardian.user.first_name} {guardian.user.last_name} has signed a consent form on behalf of their child, {child.first_name} {child.last_name}.'

            attachment = consent_pdf(consent)
            email_attachments = [
                [attachment, f'{child.first_name}_{child.last_name}_Consent.pdf'],
            ]

            with create_smtp_connection() as server:
                send_mail(
                    server=server,
                    subject=subject,
                    plain_message=message_childminder,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[os.environ['EMAIL_ADDRESS']],
                    reply_to=f'"{guardian.user.first_name} {guardian.user.last_name}" <{guardian.user.email}>',
                    attachments=email_attachments
                )
                send_mail(
                    server=server,
                    subject=subject,
                    plain_message=message_parent,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[guardian.user.email],
                    reply_to=f'\"{context["trading_name"]}\" <{os.environ["EMAIL_ADDRESS"]}>',
                    attachments=email_attachments
                )

            messages.success(request, f'Thank you for completing {child.first_name} {child.last_name}\\\'s consent form. {context["trading_name"]} will review it shortly and be in touch.')
            return redirect('child', child.pk)
    else:
        messages.error(request, f'You cannot access this page via a {request.method} request.')
        return redirect('child', child.pk)
    
# Child Record Views

@inject_context
@requires_guardian
@requires_guardians_child
def child_record_view(request, child_pk, context=None, guardian=None, child=None):
    context['child'] = child
    record = getattr(child, "record", None)
    if record is None:
        return render(request, 'child_forms/child_record.html', context)
    else:
        messages.error(request, f'A record already exists for {child.first_name} {child.last_name}.')
        return redirect('parent_dashboard')
    
@inject_context
@requires_guardian
@requires_guardians_child
def save_child_record_view(request, child_pk, context=None, guardian=None, child=None):
    if request.method == 'POST':
        record = getattr(child, "record", None)
        if record:
            messages.error(request, f'Cannot submit another record for {child.first_name} {child.last_name}.')
            return redirect('child', child.pk)
        else:
            data = request.POST
            record = ChildRecord.objects.create(
                child=child,
                home_address=data['home_address'],
                doctor_name=data['doctor_name'],
                doctor_surgery=data['doctor_surgery'],
                doctor_phone=data['doctor_phone'],
                emergency_contact1_name=data['emergency_contact1_name'],
                emergency_contact1_relationship=data['emergency_contact1_relationship'],
                emergency_contact1_phone=data['emergency_contact1_phone'],
                emergency_contact2_name=data.get('emergency_contact2_name') or None,
                emergency_contact2_relationship=data.get('emergency_contact2_relationship') or None,
                emergency_contact2_phone=data.get('emergency_contact2_phone') or None,
                medical_conditions=data.get('medical_conditions') or None,
                allergies=data.get('allergies') or None,
                dietary_needs=data.get('dietary_needs') or None,
                medication=data.get('medication') or None,
                vaccinations=data.get('vaccinations') or None,
                languages_spoken=data.get('languages_spoken') or None,
                religion_cultural_needs=data.get('religion_cultural_needs') or None,
                additional_notes=data.get('additional_notes') or None,
                parent_signature=data['parent_signature'],
                parent_ip=request.headers.get('X-Real-IP'),
            )

            # Generate PDF attachment
            attachment = child_record_pdf(record)
            email_attachments = [
                [attachment, f'{child.first_name}_{child.last_name}_Child_Record.pdf'],
            ]

            subject = f'Child Record completed for {child.first_name} {child.last_name}'
            message_parent = f'Hello {guardian.user.first_name},\n\nThank you for completing the child record form for {child.first_name}. This ensures we have up-to-date details for emergencies, health, and wellbeing.\n\nAttached is your completed copy.\n\nKind regards,\n\n{context["trading_name"]}'
            message_childminder = f'{guardian.user.first_name} {guardian.user.last_name} has completed the child record form for {child.first_name} {child.last_name}.'

            # Send both emails
            with create_smtp_connection() as server:
                send_mail(
                    server=server,
                    subject=subject,
                    plain_message=message_childminder,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[os.environ['EMAIL_ADDRESS']],
                    reply_to=f'"{guardian.user.first_name} {guardian.user.last_name}" <{guardian.user.email}>',
                    attachments=email_attachments
                )
                send_mail(
                    server=server,
                    subject=subject,
                    plain_message=message_parent,
                    from_email=os.environ['EMAIL_ADDRESS'],
                    to_emails=[guardian.user.email],
                    reply_to=f'\"{context["trading_name"]}\" <{os.environ["EMAIL_ADDRESS"]}>',
                    attachments=email_attachments
                )

            messages.success(request, f'Thank you for completing {child.first_name} {child.last_name}\\\'s child record form. {context["trading_name"]} will review it shortly.')
            return redirect('child', child.pk)

    else:
        messages.error(request, f'You cannot access this page via a {request.method} request.')
        return redirect('child', child.pk)

    

