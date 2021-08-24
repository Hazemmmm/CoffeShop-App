import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fsnd-hazem.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'cafe'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code



def get_token_auth_header():
    auth = request.headers['Authorization']
    
    # if ['Authorization'] not in request.headers:
    #     raise AuthError({"code":"authorization header missing",
    #                      "description":"authorization is expected"},401)
    
    header_parts = auth.split(' ')
  
    
    if len(header_parts)!=2:
        raise AuthError({"code":"invalid headers authorization",
                         "description":"headers must be in formats"},401)
    
    elif header_parts[0].lower() !='bearer':
        raise AuthError({"code":"not bearerToken",
                         "description":"authorization header must be bearer"},401)
        
    token = header_parts[1]
    return token



def check_permissions(permission, payload):
    if permission not in payload['permissions']:
        raise AuthError({"code":"permission is missing",
                         "description":"permmision must be in payload formnat"},401)
    return True
    

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwtks = json.loads(jsonurl.read())
 
    unverified_header = jwt.get_unverified_header(token)
   
    
    rsa_key = {}
    
    if 'kid' not in unverified_header:
        raise AuthError({"code":"invalid header","description":"authorization no formed"},401)
    
    for key in jwtks['keys']:
       
        if key['kid'] == unverified_header['kid']:
            rsa_key ={
                'kty':key['kty'],
                'kid':key['kid'],
                'use':key['use'],
                'n':key['n'],
                'e':key['e'],
                
            }
    if rsa_key:
        try:
            payload = jwt.decode(token,
                                 rsa_key,
                                 algorithms=ALGORITHMS,
                                 audience=API_AUDIENCE,
                                 issuer='https://' + AUTH0_DOMAIN + '/')
            return payload
        
        except jwt.ExpiredSignatureError: 
            raise AuthError({"code":"token expired",
                                 "description":"token expired"},401)
        except jwt.JWTClaimsError:
            raise AuthError({"code":"invalid Claims",
                                 "description":"invalid claims"},401)      
        except Exception:
            raise AuthError({"code":"invalid Header","description":"unable to parse authonication token"},400)
        
    raise AuthError({"code":"invalid_header",
                     "description":"unable to find the appropiate key"},400)
            
    
  
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator