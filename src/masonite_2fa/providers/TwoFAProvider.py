"""A TwoFAProvider Service Provider."""
from masonite.packages import PackageProvider
from masonite.configuration import config

from ..TwoFA import TwoFA


class TwoFAProvider(PackageProvider):
    def configure(self):
        """Register objects into the Service Container."""
        (self.root("masonite_2fa").name("2fa").config("config/masonite_2fa.py", publish=True))

    def register(self):
        super().register()
        two_fa = TwoFA(self.application).set_options(config("2fa"))
        self.application.bind("2fa", two_fa)

    def boot(self):
        """Boots services required by the container."""
        pass
