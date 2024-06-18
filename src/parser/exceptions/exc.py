class VkApiError(Exception):
    """Exception raised when VK API receive error.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, error_code: int, message="Vk Api error"):
        self.error_code = error_code
        self.message = message
        super().__init__(self.error_code, self.message)


class TokenError(Exception):
    """Exception raised when VK token error.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Vk token error"):
        self.message = message
        super().__init__(self.message)

