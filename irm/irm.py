# -*- coding: utf-8 -*-

import platform

import serial


PORT_LINUX = '/dev/ttyACM0'
PORT_DARWIN = '/dev/cu.usbmodem01231'
PORTS = {
    'Linux': PORT_LINUX,
    'Darwin': PORT_DARWIN,
}
BAUDRATE = 9600
TIMEOUT = 1


class NotSupportedError(Exception):
    """Raised when the platform is not supported"""
    def __init__(self, platform):
        msg = "'{}' is not supported.".format(platform)
        super(NotSupportedError, self).__init__(msg)


class IrMagician(object):

    def __init__(self, port=None):
        self.port = self.get_port() if port is None else port
        self._connected = False
        self.ir_serial = None

    @property
    def connected(self):
        return self._connected

    def _make_connection(self):
        if not self._connected:
            self.ir_serial = serial.Serial(self.port, BAUDRATE, timeout=TIMEOUT)
            self._connected = True

    def connect(self):
        self._make_connection()

    def _get_port(self):
        _platform = platform.system()
        port = PORTS.get(_platform, None)
        if port is None:
            raise NotSupportedError(_platform)
        return port

    def _write(self, data):
        self.ir_serial.write('{}\r\n'.format(data))

    def _readline(self):
        """Readline and strip"""
        return self.ir_serial.readline().strip()

    def _read(self, size):
        return self.ir_serial.read(size).strip()

    def set_bank(self, n):
        """Set memory bank(0-9)"""
        if n < 0 or n > 9:
            raise ValueError
        self._write('b,{}'.format(n))

    def capture(self):
        """Capture Signal"""
        self._write('c')

    def dump(self, n):
        """Dump memory (0-63)"""
        if n < 0 or n > 63:
            raise ValueError
        self._write('d,{}'.format(n))
        return self._read(2)
