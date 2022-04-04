import secrets
import string

alphabet = string.ascii_letters + string.digits


def generate_backup_code():
    part_one = "".join(secrets.choice(alphabet) for i in range(10))
    part_two = "".join(secrets.choice(alphabet) for i in range(10))
    return f"{part_one}-{part_two}"
