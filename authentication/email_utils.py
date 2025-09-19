from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string, get_template
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from wrestling_fed_backend.settings import DEBUG
from authentication.models import User
from authentication.tokens import account_activation_token


def send_account_confirmation_email(request, user):
    current_site = get_current_site(request)
    context = {
        'user': user,
        'domain': '{}{}'.format('://' if DEBUG else 's://',
                                current_site.domain),
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    }
    template = render_to_string('email/account_activate_email.html', context=context)
    mail = EmailMessage(subject='Confirm account for AXApp', body=template, to=[user.email])
    mail.content_subtype = 'html'
    mail.send(fail_silently=False)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        template = get_template('email/account_success_confirmation.html')
        return HttpResponse(template.render({'user': user}, request))
    else:
        return HttpResponse('Activation link is invalid!')