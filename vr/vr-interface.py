import socket, queue, threading, select, asyncio, struct, cv2, mmap, threading, collections
from time import sleep
# from win32.win32api import *
import win32
import win32pipe, win32file, pywintypes

# obtained from https://github.com/benhoyt/namedmutex
"""Named mutex handling (for Win32)."""

import ctypes
from ctypes import wintypes

"""Named mutex handling (for Win32).
See README.md or https://github.com/benhoyt/namedmutex for a bit more
documentation.
This code is released under the new BSD 3-clause license:
http://opensource.org/licenses/BSD-3-Clause
"""
# Create ctypes wrapper for Win32 functions we need, with correct argument/return types
_CreateMutex = ctypes.windll.kernel32.CreateMutexW
_CreateMutex.argtypes = [wintypes.LPCVOID, wintypes.BOOL, wintypes.LPCWSTR]
_CreateMutex.restype = wintypes.HANDLE

_WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
_WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_WaitForSingleObject.restype = wintypes.DWORD

_ReleaseMutex = ctypes.windll.kernel32.ReleaseMutex
_ReleaseMutex.argtypes = [wintypes.HANDLE]
_ReleaseMutex.restype = wintypes.BOOL

_CloseHandle = ctypes.windll.kernel32.CloseHandle
_CloseHandle.argtypes = [wintypes.HANDLE]
_CloseHandle.restype = wintypes.BOOL

class NamedMutex(object):
    """A named, system-wide mutex that can be acquired and released."""

    def __init__(self, name, acquired=False):
        """Create named mutex with given name, also acquiring mutex if acquired is True.
        Mutex names are case sensitive, and a filename (with backslashes in it) is not a
        valid mutex name. Raises WindowsError on error.
        
        """
        self.name = name
        self.acquired = acquired
        ret = _CreateMutex(None, False, name)
        if not ret:
            raise ctypes.WinError()
        self.handle = ret
        if acquired:
            self.acquire()

    def acquire(self, timeout=None):
        """Acquire ownership of the mutex, returning True if acquired. If a timeout
        is specified, it will wait a maximum of timeout seconds to acquire the mutex,
        returning True if acquired, False on timeout. Raises WindowsError on error.
        
        """
        if timeout is None:
            # Wait forever (INFINITE)
            timeout = 0xFFFFFFFF
        else:
            timeout = int(round(timeout * 1000))
        ret = _WaitForSingleObject(self.handle, timeout)
        if ret in (0, 0x80):
            # Note that this doesn't distinguish between normally acquired (0) and
            # acquired due to another owning process terminating without releasing (0x80)
            self.acquired = True
            return True
        elif ret == 0x102:
            # Timeout
            self.acquired = False
            return False
        else:
            # Waiting failed
            raise ctypes.WinError()

    def release(self):
        """Relase an acquired mutex. Raises WindowsError on error."""
        ret = _ReleaseMutex(self.handle)
        if not ret:
            raise ctypes.WinError()
        self.acquired = False

    def close(self):
        """Close the mutex and release the handle."""
        if self.handle is None:
            # Already closed
            return
        ret = _CloseHandle(self.handle)
        if not ret:
            raise ctypes.WinError()
        self.handle = None

    __del__ = close

    def __repr__(self):
        """Return the Python representation of this mutex."""
        return '{0}({1!r}, acquired={2})'.format(
                self.__class__.__name__, self.name, self.acquired)

    __str__ = __repr__

    # Make it a context manager so it can be used with the "with" statement
    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

class UnityComms:
    MAX_WRITE_DATA_LEN = 12
    # WriteData = collections.namedtuple
    def __init__(self, on_rotation=[], on_position=[]):  # on_rotation, on_position..., arrays of functions to be called when the values change
        self.to_unity_mem = mmap.mmap(0, 3, "toUnity", mmap.ACCESS_DEFAULT)
        self.from_unity_mem = mmap.mmap(0, 2+UnityComms.MAX_WRITE_DATA_LEN, "toPython1", mmap.ACCESS_DEFAULT)
        self.to_unity_mutex = NamedMutex("toUnityMut")
        self.from_unity_mutex = NamedMutex("toPythonMut1")

        self.write_queue = queue.Queue
        self.connected = False  # when false, read and write do not work.
        # headset data!
        self.hset_rotation = [0, 0, 0]
        self.hset_position = [0, 0, 0]
        #start read and write threads

        self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        self.read_thread.start()
        self.write_thread = threading.Thread(target=self.write_loop, daemon=True)
        self.write_thread.start()
        # self.read_loop()
        # print(bytes(self.from_unity_mem).hex())
        # self.read_loop()
        # while True:
        #     print(bytes(self.from_unity_mem).hex())
        #     print(struct.unpack("=fff", self.from_unity_mem[1:13]))
        #     sleep(0.1)

        # self.write_thread = threading.Thread(target=self.write, daemon=True)

    #WRITING FUNCTIONS!
    def uppdate_settings(self):
        # read delay, write delay, 
        pass

    def update_view(self, image):
        pass

    def confirm_connection(self):
        self.write_queue.put([0x01, bytearray()])

    def close_connection(self):
        self.write_queue.put([0x10, bytearray()])

    def stop_unity_reading(self):
        self.write_queue.put([0x11, bytearray()])

    def stop_execution(self):   # remove locks and inform unity of disconnect
        pass

    def update_image(self, image=None, rotation=None): # update image by updating viewImage if image is None
        # print("udating image")
        if rotation == None:
            rotation = self.hset_rotation
        if image == None:
            print(rotation)
            self.write(struct.pack("=cfff", (0x02).to_bytes(1, byteorder="big"), rotation[0], rotation[1], rotation[2]))

    def write_loop(self):
        while True:
            if not self.write_queue.empty:
                to_write = queue.get()  # write data is formated as an array (or tuple) with [command, data]
                self.write(to_write[0], to_write[1])

    def write(self, command, data):
        # maybe use queue instead
        self.to_unity_mutex.acquire()
        #add catch error
        while self.from_unity_mem[0] != 0:
            # print("acquired")
            self.to_unity_mutex.release()

            sleep(0.001)    # sleep so unity can take lock
            
            # print("released")
            #input to test
            # q = input(">")
            # if q == 'q':
            #     break
            acquired = self.to_unity_mutex.acquire(1)
        #     print("acquire: " + str(acquired))
        self.to_unity_mem[0] = 1
        self.to_unity_mem[1] = command
        # print(bytes(self.from_unity_mem[0]).hex())
        # catch when data is greater than maximumm length allowed!
        self.to_unity_mem[2:2+len(data)] = data # make sure data does not go out of bounds!
        self.to_unity_mutex.release()

    def read_loop(self):
        while True:
            self.from_unity_mutex.acquire(1)
            while self.from_unity_mem[0] != 1:
                self.from_unity_mutex.release()
                sleep(0.001)    # sleep so unity can take lock
                acquired = self.from_unity_mutex.acquire(1)

            # while self.from_unity_mem[0] != 1:
            #     sleep(0.001)    # sleep so unity can take lock
            # self.from_unity_mutex.acquire(1)

            command = self.from_unity_mem[1]
            self.from_unity_mem[0] = 0  # confirms read
            # print(bytes(self.from_unity_mem[0]).hex())
            self.from_unity_mutex.release()
            # print(command)
            match command:
                case 0x01:  # confirm existance
                    self.confirm_connection()
                case 0x10:  # close connection
                    self.stop_unity_reading()   # make unity stop reading as well
                case 0x02:  # headset position
                    self.hset_position = struct.unpack("=fff", self.from_unity_mem[2:14])
                    print("position: " + str(self.hset_position))
                case 0x03:  # headset rotation (euler angles)
                    self.hset_rotation = struct.unpack("=fff", self.from_unity_mem[2:14])
                    # print("rotation: " + str(self.hset_rotation))
                case 0x04:  # headset rotation (quaternions)
                    self.hset_quat = struct.unpack("=ffff", self.from_unity_mem[2:18])
                case 0x20:  # move front
                    pass
                case 0x21:  # move up
                    pass
                case 0x22:  # move side
                    pass
                case 0x23:  # pitch
                    pass
                case 0x24:  # yaw
                    pass
                case 0x25:  # roll
                    pass

class UnityCommsPipe:
    def __init__(self):
        self.hset_rotation = [0, 0, 0]
        self.hset_position = [0, 0, 0]
        self.hset_quat = [0, 0, 0, 0]
        self.rarm_rotation = [0, 0, 0]
        self.rarm_position = [0, 0, 0]
        self.rarm_quat = [0, 0, 0, 0]
        self.larm_rotation = [0, 0, 0]
        self.larm_position = [0, 0, 0]
        self.larm_quat = [0, 0, 0, 0]
        self.rClaw = 0
        self.lClaw = 0
        self.movements = [0, 0, 0, 0, 0, 0]

        print('unity comm start')
        # self.pipe = win32pipe.CreateNamedPipe(r'\\.\pipe\testPipe', win32pipe.PIPE_ACCESS_DUPLEX,
        # win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT
        # , 1, 65536, 65536, 300, None)
        self.pipe = win32pipe.CreateNamedPipe(r'\\.\pipe\testPipe', win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT
        , 1, 65536, 65536, 300, None)
        win32pipe.ConnectNamedPipe(self.pipe)
        print("connected pipe")
        read_thread = threading.Thread(target=self.read_loop, daemon=True)
        read_thread.start()
        self.read_loop()

    def test_write(self):
        error, data_written = win32file.WriteFile(self.pipe, bytes('test'.encode("ascii")))
        print(error)
        print(data_written)
    
    def read_loop(self):
        packet_found = False
        expected_len = 0
        command = 0
        while True:
            buffer = []
            input_data = win32file.ReadFile(self.pipe, 2048)
            print(input_data)

if __name__ == "__main__":  # simple vr-interface for test driving
    # comms = UnityComms()
    # while True:
    #     sleep(1)
    comm_pipe = UnityCommsPipe()
    while True:
        sleep(0.01)
        comm_pipe.test_write()
        val = input()
        if val == 'q':
            break
        comm_pipe.test_write()