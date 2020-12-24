class HttpException(Exception):
    def __init__(self, msg, props: dict):
        super().__init__(msg)
        self.props = props
