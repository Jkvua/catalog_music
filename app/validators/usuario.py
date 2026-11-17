import re


class UsuarioValidator:

    @staticmethod
    def validar_user(user):
        return (
            isinstance(user, str)
            and 1 <= len(user.strip()) <= 100
        )

    @staticmethod
    def validar_email(email):
        if not isinstance(email, str):
            return False

        email = email.strip()

        if not 1 <= len(email) <= 100:
            return False

        regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

        return re.fullmatch(regex, email) is not None

    @staticmethod
    def validar_password(password):
        return (
            isinstance(password, str)
            and len(password) >= 8
        )

    @staticmethod
    def validar_is_admin(is_admin):
        return isinstance(is_admin, bool)