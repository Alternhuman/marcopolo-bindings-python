__author__ = 'martin'

import six, socket

def verify_ip(ip):
        error = False
        faulty_ip = None
        reason = None
        if not isinstance(ip, six.string_types):
            error = True
            faulty_ip = ip
            reason = "IP must be a string"
            return (error, faulty_ip, reason)

        #Instead of parsing we ask the socket module
        try:
            socket.inet_aton(ip)
        except socket.error:
            error = True
            faulty_ip = ip
            reason = "Wrong IP format"
            return (error, faulty_ip, reason)
        
        try:
            first_byte = int(re.search(r"\d{3}", ip).group(0))
            if first_byte < 224 or first_byte > 239:
                error = True
                faulty_ip = ip
                reason = "The IP is not in the multicast range"
                return (error, faulty_ip, reason)
        except (AttributeError, ValueError):
            error = True
            faulty_ip = ip
            reason = "IP is not of class D"
            return (error, faulty_ip, reason)

        if ip not in self.multicast_groups:
            error = True
            faulty_ip = ip
            reason = "The instance is not a member of this group"
            return (error, faulty_ip, reason)

class Node:
    def __init__(self, address=None, services=[], multicast_group = None):
        self._address = address
        self._services = services
        self._multicast_group = multicast_group

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def services(self):
        return self._services

    @services.setter
    def services(self, value):
        self._services = value


    @property
    def multicast_group(self):
        return self._multicast_group

    @multicast_group.setter
    def multicast_group(self, value):
        self._multicast_group = value

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, value):
        self._params = value