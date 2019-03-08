from django.dispatch import receiver
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed


@receiver(email_confirmed)
def update_user_email(sender, request, email_address, **kwargs):
    email_address.user.is_active = True
    # Make new email_address primary
    email_address.set_as_primary()
    # Get rid of old email addresses
    EmailAddress.objects.filter(
        user=email_address.user
    ).exclude(primary=True).delete()


__all__ = ['update_user_email']

