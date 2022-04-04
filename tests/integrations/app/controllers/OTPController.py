"""A WelcomeController Module."""
from masonite.request import Request
from masonite.response import Response
from masonite.views import View
from masonite.controllers import Controller
from masonite.facades import Auth

from src.masonite_2fa import TwoFA, TwoFABackupCode


class OTPController(Controller):
    def account(self, view: View, request: Request):
        # log user in
        user = Auth.attempt_by_id(1)
        return view.render(
            "account",
            {
                "user": user,
                "twofa_enabled": TwoFA.enabled() and TwoFA.user_enabled(),
                "otp_secret": TwoFA.get_user_secret_key(),
                "otp_uri": TwoFA.get_uri(),
                "otp_qrcode": TwoFA.get_qr_code(),
                "otp_codes": request.session.get("2fa_codes") or [],
                "otp_codes_left": TwoFABackupCode.where("user_id", user.id)
                .where("used", False)
                .count(),
            },
        )

    def admin(self, view: View):
        """View that always requires 2FA input first."""
        return view.render("admin")

    def enable(self, request: Request, response: Response):
        """Enable 2FA for a user"""
        if TwoFA.enabled() and not TwoFA.user_enabled():
            TwoFA.start_enabling()
        return response.redirect("/")

    def disable(self, request: Request, response: Response):
        """Disable 2FA for a user (when need configuration or when totally enabled)."""
        TwoFA.disable()
        return response.redirect("/")

    def configure(self, request: Request, response: Response):
        success, codes = TwoFA.enable(request.input("code"))
        if not success:
            request.session.flash("error", "Code invalid")
        else:
            request.session.flash("2fa_codes", codes)
            request.session.flash("success", "2FA successfully configured !")
        return response.redirect("/")

    def refresh_backup_codes(self, request: Request, response: Response):
        if TwoFA.user_enabled():
            codes = TwoFA.generate_backup_codes()
            request.session.flash("2fa_codes", codes)
        return response.redirect("/")
