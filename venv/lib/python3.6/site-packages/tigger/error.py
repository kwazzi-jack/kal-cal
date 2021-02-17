import os.path

class NotInTaggedDir(Exception):
    def __init__(self, path):
        super().__init__( "'{}' is not inside a tracked directory.".format(
            os.path.abspath(path)))

class InvalidTag(Exception):
    def __init__(self, name):
        super().__init__("'{}' is not a valid tag.".format(name))
