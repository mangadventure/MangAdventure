from django.http import HttpResponseGone
from django.urls import reverse

from . import APITestBase


class APIV1Test(APITestBase):
    def test_gone(self):
        r = self.client.get(reverse('api:v1:releases'))
        assert isinstance(r, HttpResponseGone)
