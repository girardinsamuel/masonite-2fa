import pendulum
import pyotp
import qrcode
from qrcode.console_scripts import default_factories

from masonite.facades import Request, Hash, Session

from .models.TwoFABackupCode import TwoFABackupCode
from .utils import generate_backup_code


class TwoFA:
    """2FA manager class."""

    # TIMESTAMP = "otp_timestamp"
    AUTH_PASSED = "otp_passed"
    AUTH_TIMESTAMP = "otp_timestamp"

    def __init__(self, application, options={}):
        self.application = application
        self.options = options

    def set_options(self, options) -> "TwoFA":
        """Configure 2FA instance with config."""
        self.options = options
        return self

    def _session_get(self, key, default=None):
        data = Session.get(self.options.get("session_namespace")) or {}
        return data.get(key, default)

    def _session_flush(self):
        Session.delete(self.options.get("session_namespace"))

    def _session_set(self, key, value):
        existing_data = Session.get(self.options.get("session_namespace")) or {}
        existing_data.update({key: value})
        Session.set(self.options.get("session_namespace"), existing_data)

    def get_qrcode_backend(self):
        """Get configured QR Code image backend to use.
        See https://github.com/lincolnloop/python-qrcode#other-image-factories
        """
        configured_backend = self.options.get("qrcode_backend")
        backend_name = default_factories.get(configured_backend)
        # 7.4 (unreleased)
        # return get_factory(backend_name)
        module, name = backend_name.rsplit(".", 1)
        imp = __import__(module, {}, [], [name])
        image_factory = getattr(imp, name)
        return image_factory

    def get_user(self):
        return Request.user()

    def get_user_secret_key(self) -> str:
        user = self.get_user()
        return getattr(user, self.options.get("user_secret_column"))

    def enabled(self) -> bool:
        """Check is 2FA is globally enabled."""
        return self.options.get("enabled", False)

    def user_enabled(self) -> bool:
        """Check is 2FA is enabled (configuration completed) for the given user."""
        user = self.get_user()
        return bool(getattr(user, self.options.get("user_enabled_column")))

    def can_skip_auth(self):
        """Check during request flow if 2FA auth verification can be skipped."""
        return not self.enabled() or not self.user_enabled() or self.is_still_valid()

    def expired(self):
        """Check if 2FA auth is expired for given user."""
        lifetime = self.options.get("lifetime", 0) * 60
        if lifetime == 0:
            return False

        # 2FA has been given a lifetime so check against auth time
        elapsed_time = pendulum.now().int_timestamp - self._session_get(self.AUTH_TIMESTAMP, 0)
        print(elapsed_time, lifetime)
        if elapsed_time >= lifetime:
            self.logout()
            return True

        if self.options.get("keep_alive"):
            self.update_auth_time()

        return False

    def is_still_valid(self):
        """Check if 2FA is still valid for the given user."""
        return not self.expired() and self._session_get(self.AUTH_PASSED)

    def update_auth_time(self):
        """Set or update 2FA authentication time with a timestamp in seconds."""
        self._session_set(self.AUTH_TIMESTAMP, pendulum.now().int_timestamp)

    def login(self):
        """Set 2FA authentication as valid."""
        self._session_set(self.AUTH_PASSED, True)
        self.update_auth_time()

    def logout(self):
        """Log out user of 2FA."""
        print("flushed")
        self._session_flush()

    def verify(self, code: str) -> bool:
        """Verify the given code (or backup code) for the given user."""
        totp = pyotp.TOTP(self.get_user_secret_key())

        if not totp.verify(str(code)):
            # use backup code, instead
            return self.verify_backup_code(code)
        return True

    def verify_backup_code(self, code: str) -> bool:
        """Verify the given backup code for the given user."""
        user = self.get_user()
        for backup_code in TwoFABackupCode.where("user_id", user.id).where("used", False).all():
            if Hash.check(code, backup_code.code):
                backup_code.used = True
                backup_code.save()
                return True
        return False

    def generate_secret_key(self) -> str:
        """Generate a 32-character base32 secret, compatible with Google Authenticator
        and other OTP apps."""
        return pyotp.random_base32()

    def start_enabling(self):
        user = self.get_user()
        setattr(user, self.options.get("user_secret_column"), self.generate_secret_key())
        user.save()

    def enable(self, code) -> bool:
        if not self.get_user_secret_key():
            raise Exception("must user start_enabling() before.")
        user = self.get_user()
        if self.verify(code):
            unhashed_codes = []
            if self.options.get("backup_codes", False):
                unhashed_codes = self.generate_backup_codes()

            # save 2FA state
            setattr(user, self.options.get("user_enabled_column"), True)
            user.save()
            self.login()
            return True, unhashed_codes
        else:
            return False, None

    def disable(self):
        user = self.get_user()
        setattr(user, self.options.get("user_secret_column"), "")
        setattr(user, self.options.get("user_enabled_column"), False)
        user.save()
        self.logout()

    def get_uri(self):
        user = self.get_user()
        username = getattr(user, user.get_username_column())
        totp = pyotp.TOTP(self.get_user_secret_key())
        uri = totp.provisioning_uri(name=username, issuer_name=self.options.get("app_name"))
        return uri

    def get_qr_code(self):
        uri = self.get_uri()
        img = qrcode.make(uri, image_factory=self.get_qrcode_backend())
        return img.to_string().decode("utf-8")

    def generate_backup_codes(self):
        """Generate a list of 10 backup codes."""
        user = self.get_user()
        # delete eventual existing codes
        for code in TwoFABackupCode.where("user_id", user.id).all():
            code.delete()
        unhashed_codes = []
        codes = []
        for i in range(10):
            # save unhashed code to show once to user
            unhashed_code = generate_backup_code()
            unhashed_codes.append(unhashed_code)
            # save only hashed code into db
            codes.append({"code": Hash.make(unhashed_code), "user_id": user.id, "used": False})
        TwoFABackupCode.bulk_create(codes)
        return unhashed_codes
