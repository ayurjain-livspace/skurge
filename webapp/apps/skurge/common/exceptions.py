class BaseHTTPException(Exception):
    status_code = None
    error_message = None
    is_an_error_response = True

    def __init__(self, error_message, error_info=None):
        Exception.__init__(self)
        self.error_message = error_message
        if error_info is None:
            error_info = {}
        self.error_info = error_info

    def to_dict(self):
        return {'error': self.error_message, 'response': '', 'error_info': self.error_info}


class NotFoundException(BaseHTTPException):
    status_code = 404

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class InvalidInputException(BaseHTTPException):
    status_code = 400

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class UnauthorizedException(BaseHTTPException):
    status_code = 401

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class InvalidStateException(BaseHTTPException):
    status_code = 409

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class AccessDeniedException(BaseHTTPException):
    status_code = 403

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class NotAcceptableException(BaseHTTPException):
    status_code = 406

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class ConflictException(BaseHTTPException):
    status_code = 409

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class UnprocessableEntityException(BaseHTTPException):
    status_code = 422

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class RequestEntityTooLargeException(BaseHTTPException):
    status_code = 413

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class TooManyRequestsException(BaseHTTPException):
    status_code = 429

    def __init__(self, message=None, info=None):
        super().__init__(message, info)


class HttpError(BaseHTTPException):
    status_code = 500

    def __init__(self, message=None, info=None):
        super().__init__(message, info)
