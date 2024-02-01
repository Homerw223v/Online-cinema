class UserExistsInDBException(Exception):
    pass


class PasswordsDontMatchException(Exception):
    pass


class UserNotExistsInDBException(Exception):
    pass


class PasswordNotVerified(Exception):
    pass


class RefreshTokenNotExists(Exception):
    pass


class RefreshTokenExpired(Exception):
    pass


class UserAgentNotMatch(Exception):
    pass


class FingerprintNotMatch(Exception):
    pass
