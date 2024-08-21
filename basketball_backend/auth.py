from channels.db import database_sync_to_async
from account.models import Account, Token
from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack

@database_sync_to_async
def get_user(scope):
    try:
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"userid":
                account = Account.objects.get(userName=header_value.decode("latin1"))
            if header_name == b"token":
                token = header_value.decode("latin1")
        token1 = Token.objects.get(user=account).key
        if token1 == token:
            return account
        else:
            return AnonymousUser()
    except:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        scope['user'] = await get_user(scope)
        if scope['user'].is_authenticated:
            return await self.app(scope, receive, send)
        else:
            return None
