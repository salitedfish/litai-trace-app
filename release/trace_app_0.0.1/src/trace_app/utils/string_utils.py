class StringUtils:
    @staticmethod
    def is_empty(s: str):
        assert isinstance(s, str), 's is not string'
        return len(s.strip()) == 0

    @staticmethod
    def is_empty_or(*args: str):
        for s in args:
            assert isinstance(s, str), 's is not string'
            if len(args[0].strip()) == 0:
                return True
        return False
