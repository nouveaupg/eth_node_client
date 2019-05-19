import socket
import time


class UnixSocketIPCException(Exception):
    """ Error communicating with unix socket """
    pass


class UnixSocketIPCInterface:
    def __init__(self, socket_path: str, logger=None, max_attempts: int = 5, timeout: int = 2):
        self._logger = logger
        self._max_attempts = max_attempts
        self._socket_path = socket_path
        self._timeout = timeout

    def setup_socket(self):
        new_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        new_socket.connect(self._socket_path)
        new_socket.settimeout(self._timeout)
        return new_socket

    def log_info(self, message: str):
        if self._logger:
            self._logger.info(message)
        else:
            print(message)

    def log_error(self, message: str):
        if self._logger:
            self._logger.error(message)
        else:
            print(message)

    def send(self, byte_data: bytearray, expect_response: bool = True):
        _socket = self.setup_socket()
        self.log_info("Sending {0} bytes to {1}...".format(len(byte_data), self._socket_path))
        try:
            _socket.sendall(byte_data)
        except OSError:
            self.log_error("OSError: unable to send all data to socket address: " + self._socket_path)
            raise UnixSocketIPCException
        if expect_response:
            response_raw = ""
            for _ in range(self._max_attempts):
                while True:
                    try:
                        response_raw += _socket.recv(4096).decode()
                    except socket.timeout:
                        self.log_error("IPC socket timeout.")
                        # wait 2 seconds before hammering the IO system some more
                        time.sleep(self._timeout)
                        break
                if response_raw == "":
                    # retry if we didn't get a response
                    self.log_info("IPC socket no response, retrying...")
                    _socket.close()
                    _socket = self.setup_socket()
                else:
                    break
            if response_raw == "":
                raise UnixSocketIPCException
            return response_raw
        else:
            return True

    def poll(self) -> str:
        _socket = self.setup_socket()
        response_raw = ""
        for _ in range(self._max_attempts):
            while True:
                try:
                    response_raw += _socket.recv(4096).decode()
                except socket.timeout:
                    self.log_error("IPC socket timeout.")
                    # wait 2 seconds before hammering the IO system some more
                    time.sleep(self._timeout)
                    break
            if response_raw == "":
                # retry if we didn't get a response
                self.log_info("IPC socket no response, retrying...")
                _socket.close()
                _socket = self.setup_socket()
            else:
                break
        if response_raw == "":
            # raise exceptions since we didn't get a response
            raise UnixSocketIPCException
        return response_raw
