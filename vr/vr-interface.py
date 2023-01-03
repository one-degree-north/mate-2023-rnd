import socket, queue, threading, select, asyncio, struct, cv2, mmap, threading
from time import sleep

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
    def __init__(self, in_queue=None, out_queue=None, on_rotation=[], on_position=[]):  # on_rotation, on_position..., arrays of functions to be called when the values change
        self.to_unity_mem = mmap.mmap(0, 3, "toUnity", mmap.ACCESS_DEFAULT)
        self.from_unity_mem = mmap.mmap(0, 13, "toPython1", mmap.ACCESS_DEFAULT)
        self.to_unity_mutex = NamedMutex("toUnityMut")
        self.from_unity_mutex = NamedMutex("toPythonMut1")

        self.in_queue = in_queue
        self.out_queue = out_queue
        # headset data!
        self.hset_rotation = [0, 0, 0]
        self.hset_position = [0, 0, 0]
        #start read and write threads


        # self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
        # self.read_thread.start()
        print(bytes(self.from_unity_mem).hex())
        self.read_loop()
        # while True:
        #     print(bytes(self.from_unity_mem).hex())
        #     print(struct.unpack("=fff", self.from_unity_mem[1:13]))
        #     sleep(0.1)

        # self.write_thread = threading.Thread(target=self.write, daemon=True)

    def update_view(self, image):
        
        pass

    def write(self, data, position, length):
        # maybe use queue instead
        self.to_unity_mutex.acquire(1)
        #add catch error
        while self.from_unity_mem[0] != 0:
            # print("acquired")
            self.to_unity_mutex.release()
            sleep(0.01)    # sleep so unity can take lock
            # print("released")
            #input to test
            # q = input(">")
            # if q == 'q':
            #     break
            acquired = self.to_unity_mutex.acquire(1)
        #     print("acquire: " + str(acquired))
        print("rotation: " + str(self.hset_rotation))
        self.to_unity_mem[0] = 1
        print(bytes(self.from_unity_mem[0]).hex())
        self.to_unity_mem[position:position + length] = data # make sure data does not go out of bounds!
        self.to_unity_mutex.release()

    def update_image(self, image=None, rotation=None): # update image by updating viewImage if image is None
        # print("udating image")
        if rotation == None:
            rotation = self.hset_rotation
        if image == None:
            print(rotation)
            self.write(struct.pack("=cfff", (0x02).to_bytes(1, byteorder="big"), rotation[0], rotation[1], rotation[2]))

    def read_loop(self):
        while True:
            self.from_unity_mutex.acquire(1)
            while self.from_unity_mem[0] != 1:
                # print("acquired")
                self.from_unity_mutex.release()
                sleep(0.01)    # sleep so unity can take lock
                # print("released")
                #input to test
                # q = input(">")
                # if q == 'q':
                #     break
                acquired = self.from_unity_mutex.acquire(1)
            #     print("acquire: " + str(acquired))
            # print("reading data!")
            #read data!
            self.hset_rotation = struct.unpack("=fff", self.from_unity_mem[1:13])
            print("rotation: " + str(self.hset_rotation))
            self.from_unity_mem[0] = 0
            print(bytes(self.from_unity_mem[0]).hex())
            self.from_unity_mutex.release()

def test_camera(unity_comms):
    print("AAAAAA")
    # vid = cv2.VideoCapture(0)
    im = cv2.imread(r'C:\Users\gold_\Downloads\Python-logo-notext.png')
    while True:
        # ret, frame = vid.read()
        sleep(0.01)
        # cv2.imwrite(r'C:\Users\sd6tu\Documents\mate-2023-rnd\vr\unity-vr\Assets\Resources\viewImage.png', im)
        unity_comms.update_image()

if __name__ == "__main__":

    comms = UnityComms()