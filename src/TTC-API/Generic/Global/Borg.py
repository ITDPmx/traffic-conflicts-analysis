
# Borg pattern
class Borg(object):
    """ Borg pattern class"""
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state