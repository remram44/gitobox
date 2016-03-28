"""Hook server code.

Contains the :class:`~gitobox.server.Server` class which is used to communicate
with the Git hook.
"""

from __future__ import unicode_literals

import logging
import select
import socket
import sys
import time

from gitobox.utils import irange, iteritems, itervalues


class Server(object):
    """A server, that receives a bunch of lines on a TCP socket.

    Listens on a random TCP port (`port` attribute) and calls back the given
    function when the specified number of lines have been received.

    The callback gets passed the data (list of bytes objects), the connection
    and the address, so more data can be exchanged.
    """
    TIMEOUT = 5.0
    LENGTH = 1024

    def __init__(self, client_lines, callback):
        self._callback = callback
        self._client_lines = client_lines

        # Choose a port
        self._server = None
        for port in irange(15550, 15580):
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address = ('127.0.0.1', port)
            try:
                server.bind(address)
                server.listen(5)
            except socket.error:
                pass
            else:
                logging.debug("Server created on %s:%d", *address)
                self._server = server
                self.port = port
                break
        if self._server is None:
            logging.critical("Couldn't find a TCP port to listen on")
            sys.exit(1)

    def run(self):
        clients = {}

        next_timeout = None
        now = time.time()

        while True:
            sockets = [self._server]
            sockets.extend(clients)
            timeout = (None if next_timeout is None
                       else next_timeout - now + 0.2)
            rlist, _, _ = select.select(sockets, [], [],
                                        timeout)
            now = time.time()

            # Timeouts
            for sock, (data, timeout, addr) in list(iteritems(clients)):
                if now > timeout:
                    del clients[sock]
                    sock.send(b"timed out\nERROR\n")
                    sock.close()
                    logging.debug("Connection from %s timed out",
                                  addr)
                    next_timeout = -1

            for sock in rlist:
                if sock == self._server:
                    conn, addr = self._server.accept()
                    logging.debug("Connection from %s", addr)
                    timeout = now + self.TIMEOUT
                    clients[conn] = [b''], timeout, addr
                    if next_timeout is None:
                        next_timeout = timeout
                    else:
                        next_timeout = min(next_timeout, timeout)
                else:
                    data, timeout, addr = clients[conn]
                    res = conn.recv(self.LENGTH - len(data[-1]))
                    done = not res
                    if res:
                        end = res.find(b'\n')
                        while end != -1:
                            data[-1] += res[:end]
                            if len(data) == self._client_lines:
                                done = True
                                break
                            data.append(b'')
                            res = res[end+1:]
                            end = res.find(b'\n')
                        else:
                            data[-1] += res
                    if done or len(data[-1]) >= self.LENGTH:
                        del clients[conn]
                        try:
                            if len(data) == self._client_lines:
                                self._callback(data, conn, addr)
                        except Exception:
                            conn.send(b"internal server error\nERROR\n")
                            raise
                        finally:
                            conn.close()
                        next_timeout = -1

            if next_timeout == -1:
                if clients:
                    next_timeout = min(t
                                       for _, t, _ in itervalues(clients))
                else:
                    next_timeout = None
