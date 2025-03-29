import re


class Helpers:
    @staticmethod
    def is_valid_email(email: str):
        return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) is not None
