from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_302_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_405_METHOD_NOT_ALLOWED,
)

from .base import BaseTestCase


class RegistrationTest(BaseTestCase):
    """
    Test Registration
    """
    url = reverse_lazy("user-register")
    methods_not_allowed = ['patch', 'delete', 'trace']

    def test_empty_request(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("username", response.context.get('form').errors)
        self.assertIn("password1", response.context.get('form').errors)
        self.assertIn("password2", response.context.get('form').errors)
        self.assertIn("captcha", response.context.get('form').errors)
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_user(self):
        self.get_user("test@user.com")
        data = {
            "username": "test@user.com",
            "password1": "new_password",
            "password2": "new_password",
            "captcha_0": "my-test",
            "captcha_1": "PASSED",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("username", response.context.get('form').errors)
        username_error = response.context.get('form').errors["username"][0]
        self.assertEqual(
            username_error, _("A user with that email address already exists"))
        self.assertNotIn("password1", response.context.get('form').errors)
        self.assertNotIn("password2", response.context.get('form').errors)
        self.assertNotIn("captcha", response.context.get('form').errors)
        self.assertEqual(User.objects.count(), 1)

    def test_email_syntax(self):
        self.get_user("user1")
        self.get_user_token("user2")
        data = {
            "username": "test@user",
            "password1": "new_password",
            "password2": "new_password",
            "captcha_0": "my-test",
            "captcha_1": "PASSED",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertIn("username", response.context.get('form').errors)
        username_error = response.context.get('form').errors["username"][0]
        self.assertEqual(username_error, _('Enter a valid email address.'))
        self.assertNotIn("password1", response.context.get('form').errors)
        self.assertNotIn("password2", response.context.get('form').errors)
        self.assertNotIn("captcha", response.context.get('form').errors)
        self.assertEqual(User.objects.count(), 2)

    def test_success_response(self):
        self.get_user("user1@user.com")
        self.get_user_token("user2@user.com")
        data = {
            "username": "test@user.com",
            "password1": "new_password",
            "password2": "new_password",
            "captcha_0": "my-test",
            "captcha_1": "PASSED",
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTP_302_FOUND)
        self.assertEqual(response.url, reverse("home"))
        self.assertEqual(User.objects.count(), 3)
        new_user = User.objects.get(username="test@user.com")
        self.assertEqual(new_user.email, "test@user.com")
        self.assertEqual(new_user.profile.phone, None)
        self.assertEqual(new_user.profile.is_email_verified, False)