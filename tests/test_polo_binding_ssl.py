import unittest
import socket

from mock import MagicMock, patch

from marcopolo.bindings import polo
from ssl import SSLSocket

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.polo = polo.Polo(True)
        self.polo.polo_socket = MagicMock(name="socket", spec=socket.socket)
        self.polo.polo_socket.sendto.return_value = 1
        self.polo.polo_socket.recvfrom.return_value = ("{\"OK\": \"dummy\"}", 1)
        self.polo.polo_socket.recv.return_value = 1
        
        self.polo.wrappedSocket = MagicMock(name="SSLSocket", spec=SSLSocket)
        
        self.polo.wrappedSocket.send.return_value = 1
        self.polo.wrappedSocket.recv.return_value = "{\"OK\": \"dummy\"}"
        self.polo.wrappedSocket.connect = MagicMock(name="SSLSocket.connect", spec=SSLSocket.connect)
        self.polo.wrappedSocket.connect.return_value = 1

    def test_invalid_service_name(self):
        self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.publish_service, '')
        self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.publish_service, None)
        self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.publish_service, 1)

    def test_valid_service_name(self):
        service = 'dummy'
        self.assertEqual(service, self.polo.publish_service(service))

    def test_invalid_group(self):
        invalid_groups = set()
        invalid_groups.add('1.1.1.1')
        invalid_groups.add('2.2.2.2')
        invalid_groups.add('224.2.2.2')

        self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address", self.polo.publish_service, 'dummy', invalid_groups)
        invalid_groups = set()
        invalid_groups.add('224.2.2.2')
        faulty = '1.1.1.1'
        invalid_groups.add(faulty)
        
        self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address '1\.1\.1\.1'", self.polo.publish_service, 'dummy', invalid_groups)


        invalid_groups = set()
        invalid_groups.add('224.2.2.2')
        invalid_groups.add(1)
        self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address '1'",self.polo.publish_service, 'dummy', invalid_groups)

    def test_invalid_permanent(self):
        self.assertRaisesRegexp(polo.PoloException, "permanent must be boolean", self.polo.publish_service, 'dummy', permanent='False')

    def test_invalid_root(self):
        self.assertRaisesRegexp(polo.PoloException, "root must be boolean", self.polo.publish_service, 'dummy', root='True')

    def test_invalid_multiple_params(self):
        invalid_groups = set()
        invalid_groups.add('1.1.1.1')
        invalid_groups.add('2.2.2.2')
        invalid_groups.add('224.2.2.2')
        invalid_groups.add(1)

        valid_groups = set()
        valid_groups.add('224.2.2.2')
        valid_groups.add('224.2.2.3')
        valid_groups.add('224.2.2.4')

        valid_service = 'dummy'

        invalid_service = None

        valid_root = False
        valid_permanent = False

        invalid_root = 'False'
        invalid_permanent = 'False'

        self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address .*", self.polo.publish_service, 'dummy', multicast_groups=invalid_groups, permanent=invalid_permanent, root=invalid_root)
        self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.publish_service, invalid_service, multicast_groups=invalid_groups, permanent=invalid_permanent, root=invalid_root)
        self.assertRaisesRegexp(polo.PoloException, "permanent must be boolean", self.polo.publish_service, valid_service, multicast_groups=valid_groups, permanent=invalid_permanent, root=valid_root)
        self.assertRaisesRegexp(polo.PoloException, "root must be boolean", self.polo.publish_service, valid_service, multicast_groups=valid_groups, permanent=valid_permanent, root=invalid_root)

        self.assertEqual(valid_service, self.polo.publish_service(valid_service, multicast_groups=valid_groups, permanent=valid_permanent, root=valid_root))

    def test_sendto_error(self):
        self.polo.wrappedSocket.send = MagicMock(side_effect=Exception)

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                                    "Error during internal communication",
                                                    self.polo.publish_service,
                                                    'dummy')

        self.polo.wrappedSocket.send = MagicMock(return_value=-1)

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                                    "Error during internal communication",
                                                    self.polo.publish_service,
                                                    'dummy')

    def test_recvfrom_timeout(self):
        self.polo.wrappedSocket.recv = MagicMock(side_effect=socket.timeout)

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                     "Error during internal communication",
                                     self.polo.publish_service,
                                     'dummy'
                                     )

    def test_bad_response(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=('127.0.0.1'))
        self.assertRaisesRegexp(polo.PoloInternalException, 
                                    "Error during internal communication",
                                    self.polo.publish_service,
                                    'dummy'
                                    )


    def test_malformed_json(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=("["))

        self.assertRaisesRegexp(polo.PoloInternalException,
                                                    "Error during internal communication",
                                                    self.polo.publish_service,
                                                    'dummy')

    def test_valid_json(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=("{\"OK\": \"dummy\"}"))
        valid_groups = set()
        valid_groups.add('224.2.2.2')
        valid_groups.add('224.2.2.3')
        valid_groups.add('224.2.2.4')
        self.assertEqual('dummy', self.polo.publish_service("dummy"))
        self.assertEqual('dummy', self.polo.publish_service("dummy", valid_groups))

    def test_valid_response(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=("{\"OK\": \"dummy:dummy\"}"))

        self.assertEqual('dummy:dummy', self.polo.publish_service("dummy"))

    def test_error(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=("{\"Error\": \"the service already exists\"}"))

        self.assertRaisesRegexp(polo.PoloException, "Error in publishing .*: '.*'", self.polo.publish_service, "dummy")

    def test_malformed_response(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=("{"))

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                                     "Error during internal communication",
                                                     self.polo.publish_service,
                                                     "dummy")
        
        self.polo.wrappedSocket.recv = MagicMock(return_value=("{}"))
        
        self.assertRaisesRegexp(polo.PoloInternalException,
                                                     "Error during internal communication",
                                                     self.polo.publish_service,
                                                     "dummy")

class TestDeleteValidation(unittest.TestCase):
    def setUp(self):
            self.polo = polo.Polo(True)
            self.polo.polo_socket = MagicMock(name="socket", spec=socket.socket)
            self.polo.polo_socket.sendto.return_value = 1
            self.polo.polo_socket.recvfrom.return_value = ("{\"OK\": 0}", 1)
            self.polo.polo_socket.recv.return_value = 1

            self.polo.wrappedSocket = MagicMock(name="SSLSocket", spec=SSLSocket)
            self.polo.wrappedSocket.send.return_value = 1
            self.polo.wrappedSocket.recv.return_value = "{\"OK\": \"dummy\"}"
            self.polo.wrappedSocket.connect = MagicMock(name="SSLSocket.connect", spec=SSLSocket.connect)
            self.polo.wrappedSocket.connect.return_value = 1

    def test_invalid_service_name(self):
            self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.unpublish_service, '')
            self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.unpublish_service, None)
            self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.unpublish_service, 1)

    def test_invalid_group(self):
            invalid_groups = set()
            invalid_groups.add('1.1.1.1')
            invalid_groups.add('2.2.2.2')
            invalid_groups.add('224.2.2.2')

            self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address", self.polo.unpublish_service, 'dummy', invalid_groups)
            invalid_groups = set()
            invalid_groups.add('224.2.2.2')
            faulty = '1.1.1.1'
            invalid_groups.add(faulty)

            self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address '1\.1\.1\.1'", self.polo.unpublish_service, 'dummy', invalid_groups)


            invalid_groups = set()
            invalid_groups.add('224.2.2.2')
            invalid_groups.add(1)
            self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address '1'",self.polo.unpublish_service, 'dummy', invalid_groups)

    def test_invalid_delete_file(self):
            self.assertRaisesRegexp(polo.PoloException, "delete_file must be boolean", self.polo.unpublish_service, 'dummy', delete_file='False')


    def test_invalid_multiple_params(self):
            invalid_groups = set()
            invalid_groups.add('1.1.1.1')
            invalid_groups.add('2.2.2.2')
            invalid_groups.add('224.2.2.2')
            invalid_groups.add(1)

            valid_groups = set()
            valid_groups.add('224.2.2.2')
            valid_groups.add('224.2.2.3')
            valid_groups.add('224.2.2.4')

            valid_service = 'dummy'

            invalid_service = None

            valid_delete_file = False

            invalid_delete_file = 'False'

            self.assertRaisesRegexp(polo.PoloException, "Invalid multicast group address .*", self.polo.unpublish_service, 'dummy', multicast_groups=invalid_groups, delete_file=invalid_delete_file)
            self.assertRaisesRegexp(polo.PoloException, "The name of the service .* is invalid", self.polo.unpublish_service, invalid_service, multicast_groups=invalid_groups, delete_file=invalid_delete_file)
            self.assertRaisesRegexp(polo.PoloException, "delete_file must be boolean", self.polo.unpublish_service, valid_service, multicast_groups=valid_groups, delete_file=invalid_delete_file)

            self.assertEqual('dummy', self.polo.unpublish_service(valid_service, multicast_groups=valid_groups, delete_file=valid_delete_file))


    def test_sendto_error(self):
        self.polo.wrappedSocket.send = MagicMock(side_effect=Exception)

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                                        "Error during internal communication",
                                                        self.polo.unpublish_service,
                                                        'dummy')

        self.polo.wrappedSocket.send = MagicMock(return_value=-1)

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                                        "Error during internal communication",
                                                        self.polo.unpublish_service,
                                                        'dummy')

    def test_recvfrom_timeout(self):
        self.polo.wrappedSocket.recv = MagicMock(side_effect=socket.timeout)

        self.assertRaisesRegexp(polo.PoloInternalException, 
                                        "Error during internal communication",
                                        self.polo.unpublish_service,
                                        'dummy'
                                        )

    def test_bad_response(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=(-1))
        self.assertRaisesRegexp(polo.PoloInternalException, 
                                        "Error during internal communication",
                                        self.polo.unpublish_service,
                                        'dummy'
                                        )


    def test_bad_unicode(self):
        self.polo.wrappedSocket.recv = MagicMock(return_value=1)
        self.assertRaisesRegexp(polo.PoloInternalException, 
                                        "Error during internal communication",
                                        self.polo.unpublish_service,
                                        'dummy'
                                        )

class TestServiceInfo(unittest.TestCase):
    def setUp(self):
        self.polo = polo.Polo(True)
        self.polo.polo_socket = MagicMock(name="socket", spec=socket.socket)
        self.polo.polo_socket.sendto.return_value = 1
        self.polo.polo_socket.recvfrom.return_value = ("{\"OK\": \"dummy\"}", 1)
        self.polo.polo_socket.recv.return_value = 1
        
        self.polo.wrappedSocket = MagicMock(name="SSLSocket", spec=SSLSocket)
        
        #self.polo.wrappedSocket.send.return_value = 1
        #self.polo.wrappedSocket.recv.return_value = "{\"OK\": \"dummy\"}"
        self.polo.wrappedSocket.connect = MagicMock(name="SSLSocket.connect", spec=SSLSocket.connect)
        self.polo.wrappedSocket.connect.return_value = 1

    def test_wrong_service_id(self):
        self.assertRaisesRegexp(polo.PoloException, 
                          "The name of the service .* is invalid",
                          self.polo.service_info,
                          1)

    @unittest.skip("Mock is not working yet")
    @patch('json.JSONEncoder')
    def test_json_encoding_error(self, JSONEncoder_mock):
        JSONEncoder_mock = MagicMock()

        json_mock = MagicMock(side_effect=Exception)
        json_mock.encode = MagicMock(side_effect=Exception)
        
        JSONEncoder_mock.return_value = json_mock


        self.assertRaisesRegexp(polo.PoloInternalException,
                                "Error in JSON Encoder",
                                self.polo.service_info,
                                'dummy')
        #polo.Polo.json.JSONEncoder = MagicMock()

    @unittest.skip("")
    def test_error_sending(self):
        self.polo.wrappedSocket.send = MagicMock(return_value = -1)
        self.polo.wrappedSocket.send.return_value = -1

        self.assertRaisesRegexp(polo.PoloInternalException,
                               'Error on send',
                                self.polo.service_info,
                                'dummy'
                               )

    @unittest.skip("Not working")
    def test_timeout(self):
        self.polo.wrappedSocket.send = MagicMock(return_value = 10)
        self.polo.wrappedSocket.send.return_value = 10

        self.polo.wrappedSocket.recv = MagicMock(side_effect=socket.timeout)
        self.polo.wrappedSocket.recv.side_effect = socket.timeout
        
        self.assertRaisesRegexp(polo.PoloInternalException,
                               'Timeout for reception',
                                self.polo.service_info,
                                'dummy'
                               )
    @unittest.skip("")
    def test_error_code(self):
        self.polo.wrappedSocket.send = MagicMock(return_value=10, side_effect=None)
        self.polo.wrappedSocket.send.return_value = 10

        self.polo.wrappedSocket.recv = MagicMock(return_value='{"Error":"Could not find service"}'.encode('utf-8'))
        self.assertEqual(None, self.polo.service_info('dummy'))

    @unittest.skip("")
    def test_bad_return_value(self):
        self.polo.wrappedSocket = None
        #self.polo.wrappedSocket = MagicMock()
        #self.polo.wrappedSocket.send = MagicMock(return_value = 10)
        #self.polo.wrappedSocket.send.return_value = 10

        self.assertRaisesRegexp(polo.PoloInternalException,
                                "The return value is not valid",
                                self.polo.service_info,
                                'dummy')

    def test_good_return_value(self):
        pass

    def test_missing_values(self):
        pass



class TestHasService(unittest.TestCase):
    def setUp(self):
        self.polo = polo.Polo(True)
        
        self.polo.wrappedSocket = MagicMock(name="SSLSocket", spec=SSLSock)

        self.polo.wrappedSocket.connect = MagicMock(name="SSLSocket.connect", spec=SSLSocket.connect)
        self.polo.wrappedSocket.connect.return_value = 1