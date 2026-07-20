class DomainException(Exception):
    pass


class SessionNotRunningException(DomainException):
    pass


class PlayerAlreadyConnectedException(DomainException):
    pass


class PlayerNotConnectedException(DomainException):
    pass


class InvalidControlModeException(DomainException):
    pass


class InvalidSessionStateException(DomainException):
    pass


class VoteAlreadyRunningException(DomainException):
    pass
