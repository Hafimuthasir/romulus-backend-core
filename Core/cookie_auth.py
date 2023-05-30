from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    def get_raw_token(self, request):
        # Retrieve the token from the cookie
        token = request.COOKIES.get('jwt')
        print(token)
        return token