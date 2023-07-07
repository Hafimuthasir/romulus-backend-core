from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        authorization_header = request.META['HTTP_AUTHORIZATION']
        
        if authorization_header:
            token_type, access_token = authorization_header.split()

            jwt_auth = JWTAuthentication()     
            payload = jwt_auth.get_validated_token(access_token)
            user = jwt_auth.get_user(payload)  
            if user.is_authenticated:
                if user.is_admin:
                    return True
    
        return False 
    
class IsUser(BasePermission):
    def has_permission(self, request, view):
        authorization_header = request.META['HTTP_AUTHORIZATION']
        
        if authorization_header:
            token_type, access_token = authorization_header.split()

            jwt_auth = JWTAuthentication()     
            payload = jwt_auth.get_validated_token(access_token)
            user = jwt_auth.get_user(payload)  
            if user.is_authenticated:
                if not user.is_admin:
                    return True
    
        return False 