
class UserError(Exception):
    pass


class BackEndError(Exception):
    pass


class ApiError(BackEndError):
    pass


class GrinError(Exception):
    pass

