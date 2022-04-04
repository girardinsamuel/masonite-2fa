from masonite.middleware import Middleware
from ..TwoFAFacade import TwoFA


class TwoFAMiddleware(Middleware):
    """Middleware to add 2FA additional step after login."""

    def before(self, request, response):

        if not request.user():
            return response.redirect(name="login")

        # check if user need to check oauth
        if not TwoFA.can_skip_auth():
            return response.redirect(name="login.2fa")

        return request

    def after(self, request, response):
        return request
