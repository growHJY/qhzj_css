class Response:
    def __init__(self, status: int, message: str, param) -> None:
        self.status = status
        self.message = message
        self.param = param

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "message": self.message,
            "param": self.param
        }
