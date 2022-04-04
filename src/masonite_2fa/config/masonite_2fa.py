"""Masonite 2FA Settings"""


ENABLED = True
BACKUP_CODES = True

USER_ENABLED_COLUMN = "twofa_enabled"
USER_SECRET_COLUMN = "twofa_secret"
SESSION_NAMESPACE = "twofa"

# in mn
LIFETIME = 0
KEEP_ALIVE = False

APP_NAME = "Masonite 2FA test"
QRCODE_BACKEND = "svg"
