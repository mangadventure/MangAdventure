from allauth.account.models import EmailAddress, EmailConfirmation
from pytest import fixture

from . import UsersTestBase


@fixture
def mock_allauth_adapter(monkeypatch):
    class MockAdapter:
        def confirm_email(self, *args):
            pass

        def send_confirmation_mail(self, *args):
            pass

    monkeypatch.setattr("allauth.account.models.get_adapter",
                        lambda x: MockAdapter())


class TestEmailConfirmationReceiver(UsersTestBase):
    def setup_method(self):
        super().setup_method()
        self.user.is_active = False
        self.user.save()

    def test_receiver(self, mock_allauth_adapter):
        address1 = EmailAddress.objects.create(user=self.user,
                                               email="test1@example.com",
                                               verified=False,
                                               primary=False)
        EmailAddress.objects.create(user=self.user,
                                    email="test2@example.com",
                                    verified=True,
                                    primary=True)
        EmailAddress.objects.create(user=self.user,
                                    email="test3@example.com",
                                    verified=False,
                                    primary=False)
        confirmation = EmailConfirmation.create(address1)
        confirmation.send()
        confirmation.confirm(None)
        assert not EmailAddress.objects.filter(user=self.user,
                                               email="test3@example.com")
        assert not EmailAddress.objects.filter(user=self.user,
                                               email="test2@example.com")
        address1.refresh_from_db()
        assert address1.primary
        assert self.user.is_active
