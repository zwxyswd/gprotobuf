#!/usr/bin/env python
#encoding:utf-8
'''
FileName: iostream.py
Author: smallarcher
Date: 2011/04/16 21:43:07
Commnet: 
'''

import logging
import errno
import gevent
from gevent import socket

class IOStream(object):
    """
    """
    
    def __init__(self, socket, max_buffer_size=104857600,
                 read_chunk_size=4096):
        """
        """
        self.socket = socket
        self.socket.setblocking(False)
        self.max_buffer_size = max_buffer_size
        self.read_chunk_size = read_chunk_size
        self._read_buffer = ""
        self._write_buffer = ""
        self._read_bytes = None
        self._read_callback = None
        self._write_callback = None
        self._close_callback = None
        self._state = gevent.core.EV_READ | gevent.core.EV_WRITE #| gevent.core.EV_ERROR
        self._gevent = gevent.core.event(gevent.core.EV_PERSIST | self._state,
                                         self.socket.fileno(), self._handle_events)
        self._gevent.add()

    def read_bytes(self, num_bytes, callback):
        """Call callback when we read the given number of bytes."""
        if len(self._read_buffer) >= num_bytes:
            callback(self._consume(num_bytes))
            return
        self._check_closed()
        self._read_bytes = num_bytes
        self._read_callback = callback

    def write(self, data, callback=None):
        """Write the given data to this stream.

        If callback is given, we call it when all of the buffered write
        data has been successfully written to the stream. If there was
        previously buffered write data and an old write callback, that
        callback is simply overwritten with this new callback.
        """
        self._check_closed()
        self._write_buffer += data
        self._write_callback = callback

    def set_close_callback(self, callback):
        """Call the given callback when the stream is closed."""
        self._close_callback = callback

    def close(self):
        """Close this stream."""
        if self.socket is not None:
            self._gevent.cancel()
            self.socket.close()
            self.socket = None
            if self._close_callback:
                self._run_callback(self._close_callback)

    def reading(self):
        """Returns true if we are currently reading from the stream."""
        return self._read_callback is not None

    def writing(self):
        """Returns true if we are currently writing to the stream."""
        return len(self._write_buffer) > 0

    def closed(self):
        return self.socket is None

    def _handle_events(self, fd, evtype):
        if not self.socket:
            logging.warning("Got evtype for closed stream %d", fd)
            return
        if evtype & gevent.core.EV_READ:
            self._handle_read()
        if not self.socket:
            return
        if evtype & gevent.core.EV_WRITE:
            self._handle_write()
        if not self.socket:
            return
        '''
        if evtype & gevent.core.EV_ERROR:
            self.close()
            return
        '''
        
    def _run_callback(self, callback, *args, **kwargs):
        try:
            callback(*args, **kwargs)
        except:
            # Close the socket on an uncaught exception from a user callback
            # (It would eventually get closed when the socket object is
            # gc'd, but we don't want to rely on gc happening before we
            # run out of file descriptors)
            self.close()
            # Re-raise the exception so that IOLoop.handle_callback_exception
            # can see it and log the error
            raise

    def _handle_read(self):
        try:
            chunk = self.socket.recv(self.read_chunk_size)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                return
            else:
                logging.warning("Read error on %d: %s",
                                self.socket.fileno(), e)
                self.close()
                return
        if not chunk:
            self.close()
            return
        self._read_buffer += chunk
        if len(self._read_buffer) >= self.max_buffer_size:
            logging.error("Reached maximum read buffer size")
            self.close()
            return
        if self._read_bytes:
            if len(self._read_buffer) >= self._read_bytes:
                num_bytes = self._read_bytes
                callback = self._read_callback
                self._read_callback = None
                self._read_bytes = None
                self._run_callback(callback, self._consume(num_bytes))

    def _handle_write(self):
        while self._write_buffer:
            try:
                num_bytes = self.socket.send(self._write_buffer)
                self._write_buffer = self._write_buffer[num_bytes:]
            except socket.error, e:
                if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                    break
                else:
                    logging.warning("Write error on %d: %s",
                                    self.socket.fileno(), e)
                    self.close()
                    return
        if not self._write_buffer and self._write_callback:
            callback = self._write_callback
            self._write_callback = None
            self._run_callback(callback)

    def _consume(self, loc):
        result = self._read_buffer[:loc]
        self._read_buffer = self._read_buffer[loc:]
        return result

    def _check_closed(self):
        if not self.socket:
            raise IOError("Stream is closed")

        
