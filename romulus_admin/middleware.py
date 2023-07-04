from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class CookieJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        jwt_auth = JWTAuthentication()
        if 'access_token' in request.COOKIES:
            access_token = request.COOKIES['access_token']
            try:
                payload = jwt_auth.get_validated_token(access_token)
                user = jwt_auth.get_user(payload)
                if not user.is_authenticated:
                    
                    raise exceptions.AuthenticationFailed('User not authenticated.')
                    
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except exceptions.AuthenticationFailed:
                refresh_token = request.COOKIES.get('refresh_token')
                if refresh_token:
                    try:
                        token = RefreshToken(refresh_token)
                        if token.payload['exp'] < timezone.now().timestamp():
                            raise exceptions.AuthenticationFailed('Refresh token expired.')
                        user = User.objects.get(id=token.payload['user_id'])
                        new_access_token = str(token.access_token)
                        request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                        response = self.get_response(request)
                        response.set_cookie(
                            key='access_token',
                            value=new_access_token,
                            httponly=True,
                        )
                        return response
                    except (User.DoesNotExist, exceptions.AuthenticationFailed):
                        pass
        
        response = self.get_response(request)
        return response
