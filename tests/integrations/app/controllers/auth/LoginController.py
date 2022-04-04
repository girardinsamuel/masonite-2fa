from masonite.controllers import Controller
from masonite.views import View
from masonite.request import Request
from masonite.response import Response
from masonite.authentication import Auth
from masonite.facades import Session

from src.masonite_2fa import TwoFA


class LoginController(Controller):
    def show(self, view: View):
        return view.render("auth.login")

    def two_fa(self, view: View, request: Request):
        return view.render("auth.login_2fa")

    def store(self, request: Request, auth: Auth, response: Response):
        login = auth.attempt(request.input("username"), request.input("password"))

        if login:
            return response.redirect(name="auth.home")

        # Go back to login page
        return response.redirect(name="login").with_errors(
            ["The email or password is incorrect"]
        )

    def check_2fa(self, request: Request, auth: Auth, response: Response):

        if TwoFA.verify(request.input("code")):
            TwoFA.login()
            redirect_url = TwoFA._session_get("next")
            if redirect_url:
                return response.redirect(redirect_url)
            return response.redirect(name="auth.home")

        # Go back to 2FA login page
        return response.redirect(name="login.2fa").with_errors(["The code is invalid"])

    def logout(self, auth: Auth, response: Response):
        auth.logout()
        TwoFA.logout()
        return response.redirect(name="login")
