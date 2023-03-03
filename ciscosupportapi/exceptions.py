class CiscoSupportApiException(Exception):
    def __init__(self, error):
        self.error = error
        self.message = str(error)
        super().__init__(self.message)
