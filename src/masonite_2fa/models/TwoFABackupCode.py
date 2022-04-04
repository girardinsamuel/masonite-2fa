from masoniteorm.models import Model


class TwoFABackupCode(Model):
    """TwoFABackupCode Model"""

    __table__ = "twofa_backup_codes"
    __fillable__ = ["code", "used"]
    __visible__ = ["used"]
