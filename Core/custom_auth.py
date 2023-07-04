from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from dataclasses import dataclass

@dataclass
class UserTokenPair:
    user: get_user_model()
    token: str

class CustomAdminAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest) -> UserTokenPair:
        token = request.COOKIES.get('jwt_token')
        if not token:
            return None
        try:
            user = get_user_model().objects.get(auth_token=token)
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not user.is_admin:
            raise AuthenticationFailed('User is not an admin')
        return UserTokenPair(user=user, token=token)

    def authenticate_header(self, request: HttpRequest) -> str:

        return 'Bearer'