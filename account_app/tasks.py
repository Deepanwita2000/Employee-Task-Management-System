from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


@shared_task
def send_verification_email_task(user_id, mail_subject, email_template, domain):
    print("send_verification_email_task:   inside celery...")

    user = User.objects.get(id=user_id)

    message = render_to_string(email_template, {
        'user': user,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    mail = EmailMessage(
        mail_subject,
        message,
        from_email,
        to=[to_email]
    )

    mail.content_subtype = "html"
    mail.send()

    return f"Verification email sent to {to_email}"


@shared_task
def send_otp_email_task(user_id, mail_subject, email_template, otp_code, domain):

    user = User.objects.get(id=user_id)

    message = render_to_string(email_template, {
        'user': user,
        'domain': domain,
        'code': otp_code,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user),
    })

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    mail = EmailMessage(
        mail_subject,
        message,
        from_email,
        to=[to_email]
    )

    mail.content_subtype = "html"
    mail.send()

    return f"OTP email sent to {to_email}"
