class Service(object):
    def __init__(self):
        pass

    @property
    def identifier(self):
        return self._id

    @identifier.setter
    def id(self, value):
        self._id = value

    @property
    def multicast_groups(self):
        return self._multicast_groups

    @multicast_groups.setter
    def multicast_groups(self, value):
        self._multicast_groups = value

    @property
    def params(self):
        return self._params
    
    @params.setter
    def params(self, value):
        self._params = value

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        self._disabled = value
    
    
