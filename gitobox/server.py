from __future__ import unicode_literals

import logging
import select
import socket
import time

from gitobox.utils import iteritems, itervalues


class Server(object):
    TIMEOUT = 5.0
    LENGTH = 1024

    def __init__(self, port, callback):
        self._callback = callback
        self._port = port

    def run(self):
        clients = {}

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = ('127.0.0.1', self._port)
        server.bind(address)
        server.listen(5)
        logging.debug("Server created on %s:%d", *address)

        next_timeout = None
        now = time.time()

        while True:
            sockets = [server]
            sockets.extend(clients)
            timeout = (None if next_timeout is None
                       else next_timeout - now + 0.2)
            rlist, _, _ = select.select(sockets, [], [],
                                        timeout)
            now = time.time()

            # Timeouts
            for sock, (data, timeout, addr) in list(iteritems(clients)):
                if now > timeout:
                    del clients[conn]
                    conn.send(b"timed out\nERROR\n")
                    conn.close()
                    logging.debug("Connection from %s timed out",
                                  addr)
                    next_timeout = -1

            for sock in rlist:
                if sock == server:
                    conn, addr = server.accept()
                    logging.debug("Connection from %s", addr)
                    timeout = now + self.TIMEOUT
                    clients[conn] = b'', timeout, addr
                    if next_timeout is None:
                        next_timeout = timeout
                    else:
                        next_timeout = min(next_timeout, timeout)
                else:
                    data, timeout, addr = clients[conn]
                    res = conn.recv(self.LENGTH - len(data))
                    if res:
                        end = res.find(b'\n')
                        if end != -1:
                            end += len(data)
                            data += res[:end]
                            res = None
                        else:
                            data += res
                    if not res or len(data) >= self.LENGTH:
                        del clients[conn]
                        try:
                            self._callback(data, conn, addr)
                        except Exception:
                            conn.send(b"internal server error\nERROR\n")
                            raise
                        finally:
                            conn.close()
                        next_timeout = -1
                    else:
                        clients[conn] = data, timeout, addr

            if next_timeout == -1:
                if clients:
                    next_timeout = min(t
                                       for _, t, _ in itervalues(clients))
                else:
                    next_timeout = None
