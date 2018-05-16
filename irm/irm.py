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


def validate(value, _range):
    if value not in _range:
        raise ValueError


class IrMagician(object):

    def __init__(self, port=None):
        self.port = self._get_port() if port is None else port
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
        validate(n, range(10))
        self._write('b,{}'.format(n))

    def capture(self):
        """Capture Signal"""
        self._write('c')

    def dump(self, n):
        """Dump memory (0-63)"""
        validate(n, range(64))
        self._write('d,{}'.format(n))
        return self._read(2)

    def _error_correction_check(self):
        self._write('e')

    def information(self, n):
        validate(n, range(8))
        self._write('i,{}'.format(n))
        return self._readline()

    def set_pos_scaler(self, n):
        validate(n, range(1,256))
        self._write('k,{}'.format(n))
        return self._readline()

    def on_led(self):
        self._write('l,1')
        return self._readline()

    def off_led(self):
        self._write('l,0')
        return self._readline()

    def change_modulation(self, n):
        validate(n, range(3))
        self._write('m,{}'.format(n))
        return self._readline()

    def set_record_pointer(self, n):
        validate(n, range(65536))
        self._write('n,{}'.format(n))
        return self._readline()

    def play(self):
        self._write('p')

    def reset(self, n):
        validate(n, range(2))
        self._write('r,{}'.format(n))
        return self._readline()

    def _statics_mode(self):
        self._write('s')
        return self._readline()

    def _raw_temp(self):
        self._write('t')
        t = self._readline()
        self._readline()  # clear buffer
        return t

    def temp(self):
        try:
            t = self._convert_temp(int(self._raw_temp()))
        except ValueError:
            t = -273
        return t

    @staticmethod
    def _convert_temp(n):
        return ((5 / 1024 * n) - 0.4) / (19.53 / 1000)

    def version(self):
        self._write('v')
        result = self._readline()
        self._readline()  # should be 'OK'
        return self._readline()

    def write(self, pos, data):
        validate(pos, range(64))
        validate(data, range(256))
        self._write('w,{},{}'.format(pos, data))
