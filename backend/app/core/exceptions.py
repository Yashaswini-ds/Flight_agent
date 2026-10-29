from fastapi import HTTPException, status

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials or unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Permission denied for this operation"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Requested resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class ConflictException(HTTPException):
    def __init__(self, detail: str = "Resource conflict or duplicate operation"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
