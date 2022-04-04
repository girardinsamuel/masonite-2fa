from masonite.middleware import Middleware
from masonite.facades import Session
from ..TwoFAFacade import TwoFA


class ForceTwoFAMiddleware(Middleware):
    """Middleware to force 2FA step before accessing a given route."""

    def before(self, request, response):

        if not request.user():
            return response.redirect(name="login")

        # save route path
        TwoFA._session_set("next", request.get_path())
        return response.redirect(name="login.2fa").with_errors("errors", "Need re-auth !")

    def after(self, request, response):
        import pdb

        pdb.set_trace()
        return request
