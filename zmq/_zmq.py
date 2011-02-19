"""
Low-level ctypes binding for the ZeroMQ library. Makes an attempt to
emulate pyzmq.core.

Daniel Holth <dholth@fastmail.fm>
"""

from ctypes import *
from ctypes_configure import configure

class CConfigure(object):
    _compilation_info_ = configure.ExternalCompilationInfo(
            includes = ['zmq.h'],
            libraries = ['zmq']
            )
    size_t = configure.SimpleType('size_t', c_int)
    
for cname in ['ZMQ_AFFINITY', 'ZMQ_DOWNSTREAM', 'EADDRINUSE',
    'EADDRNOTAVAIL', 'EAGAIN', 'ECONNREFUSED', 'EFAULT', 'EFSM',
    'EINPROGRESS', 'EINVAL', 'EMTHREAD', 'ENETDOWN', 'ENOBUFS',
    'ENOCOMPATPROTO', 'ENODEV', 'ENOMEM', 'ENOTSUP', 'EPROTONOSUPPORT',
    'ETERM', 'ZMQ_FORWARDER', 'ZMQ_HWM', 'ZMQ_IDENTITY', 'ZMQ_MCAST_LOOP',
    'ZMQ_NOBLOCK', 'ZMQ_PAIR', 'ZMQ_POLLERR', 'ZMQ_POLLIN', 'ZMQ_POLLOUT',
    'ZMQ_PUB', 'ZMQ_PULL', 'ZMQ_PUSH', 'ZMQ_QUEUE', 'ZMQ_RATE', 'ZMQ_RCVBUF',
    'ZMQ_RCVMORE', 'ZMQ_RECOVERY_IVL', 'ZMQ_REP', 'ZMQ_REQ', 'ZMQ_SNDBUF',
    'ZMQ_SNDMORE', 'ZMQ_STREAMER', 'ZMQ_SUB', 'ZMQ_SUBSCRIBE', 'ZMQ_SWAP',
    'ZMQ_UNSUBSCRIBE', 'ZMQ_UPSTREAM', 'ZMQ_XREP', 'ZMQ_XREQ', 'ZMQ_MAX_VSM_SIZE']:
        pyname = cname.split('_', 1)[-1]
        setattr(CConfigure, pyname, configure.ConstantInteger(cname))

info = configure.configure(CConfigure)
globals().update(info)

class ZMQError(Exception):
    pass

def _check_nonzero(result, func, arguments):
    if result.value != 0:
        raise ZMQError()
    return result

def _check_null(result, func, arguments):
    if zmq_errno():
        raise ZMQError()
    return result

libzmq = cdll.LoadLibrary("libzmq.so")

libzmq.zmq_version.restype = None
libzmq.zmq_version.argtypes = [POINTER(c_int)]*3

major = c_int()
minor = c_int()
patch = c_int()

libzmq.zmq_version(byref(major), byref(minor), byref(patch))

__version__ = tuple((x.value for x in (major, minor, patch)))

# Error number as known by the 0MQ library

libzmq.zmq_errno.argtypes = []

libzmq.zmq_strerror.restype = c_char_p
libzmq.zmq_strerror.argtypes = [c_int]

# 0MQ infrastructure

class Context(object):
    def __init__(self, threads=1):                
        self.ctx = zmq_init(threads) 

libzmq.zmq_init.restype = c_void_p
libzmq.zmq_init.argtypes = [c_int]
libzmq.zmq_init.errcheck = _check_null

libzmq.zmq_term.restype = c_int
libzmq.zmq_term.argtypes = [c_void_p]

# 0MQ message definition

class zmq_msg_t(Structure):
    _fields_ = [
            ('content', c_void_p),
            ('flags', c_ubyte),
            ('vsm_size', c_ubyte),
            ('vsm_data', c_ubyte*MAX_VSM_SIZE)
            ]

libzmq.zmq_msg_init.argtypes = [POINTER(zmq_msg_t)]
libzmq.zmq_msg_init_size.argtypes = [POINTER(zmq_msg_t), size_t]

# requires a free function:
libzmq.zmq_msg_init_data.argtypes = [POINTER(zmq_msg_t), c_void_p, size_t,
                                     c_void_p, c_void_p]
libzmq.zmq_msg_close.argtypes = [POINTER(zmq_msg_t)]
libzmq.zmq_msg_move.argtypes = [POINTER(zmq_msg_t), POINTER(zmq_msg_t)]
libzmq.zmq_msg_copy.argtypes = [POINTER(zmq_msg_t), POINTER(zmq_msg_t)]
libzmq.zmq_msg_data.restype = c_void_p
libzmq.zmq_msg_data.argtypes = [POINTER(zmq_msg_t)]
libzmq.zmq_msg_size.restype = c_void_p
libzmq.zmq_msg_size.argtypes = [POINTER(zmq_msg_t)]

# 0MQ socket definition

libzmq.zmq_socket.restype = c_void_p
libzmq.zmq_socket.argtypes = [c_void_p, c_int]

libzmq.zmq_close.argtypes = [c_void_p]

libzmq.zmq_setsockopt.argtypes = [c_void_p, c_int, c_void_p, size_t]
libzmq.zmq_getsockopt.argtypes = [c_void_p, c_int, c_void_p, size_t]
libzmq.zmq_bind.argtypes = [c_void_p, c_char_p]
libzmq.zmq_connect.argtypes = [c_void_p, c_char_p]
libzmq.zmq_send.argtypes = [c_void_p, POINTER(zmq_msg_t), c_int]
libzmq.zmq_recv.argtypes = [c_void_p, POINTER(zmq_msg_t), c_int]

def _shortcuts():
    for symbol in dir(libzmq):
        if symbol.startswith('zmq_'):
            globals()[symbol] = getattr(libzmq, symbol)

_shortcuts()
