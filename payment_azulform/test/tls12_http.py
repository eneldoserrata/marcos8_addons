'''
This module allows use of HTTPS using TLS v1.2 via OpenSSL v1.0.1.  Note that this requires 
a PyOpenSSL build with support for TLS 1.2 methods.  See 
https://github.com/enernoc/pyopenssl for a suitable fork.
'''

__all__ = ['TLS1_2AuthHandler']

import socket, ssl
import urllib2
import httplib
import logging

from OpenSSL import SSL

DEFAULT_REQUEST_TIMEOUT = 5.0

# TLS v1.2 classes.
class TLS1_2AuthHandler(urllib2.HTTPSHandler):
    '''
    HTTPS handler that uses TLSv1.2 and verifies the server cert
    '''

    def __init__(self, key, cert, ca_certs, ssl_version=SSL.TLSv1_2_METHOD, ciphers=None):
        '''
        Inlitlize the Client Authentication Handler.

        Args:
            key: SSL key
            cert: SSL certificate
            ca_certs: CA Certificates
            ssl_Version: Version of SSL we are using (default: SSL.TLSv1_2_METHOD)
            cipher: Which ciphers we are using (default: None)
        '''
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
        self.ca_certs = ca_certs
        self.ssl_version = ssl_version
        self.ciphers = ciphers

    def https_open(self, req):
        '''
        Rather than pass in a reference to a connection class, we pass in
        a reference to a function which, for all intents and purposes,
        will behave as a constructor
        '''
        return self.do_open(self.get_connection, req)

    def get_connection(self, host, timeout=DEFAULT_REQUEST_TIMEOUT):
        '''
        Get's the Authenticated HTTP connection.

        Args:
            host: we are connecting to.
            timeout: Connection timeout (in seconds)
        '''
        return TLS1_2Connection( host, 
                key_file = self.key, 
                cert_file = self.cert,
                timeout = timeout,
                ciphers = self.ciphers,
                ca_certs = self.ca_certs, 
                ssl_version = self.ssl_version )


class TLS1_2Connection(httplib.HTTPSConnection):
    '''
    Overridden to allow peer certificate validation, configuration
    of SSL/ TLS version and cipher selection.  See:
    http://hg.python.org/cpython/file/c1c45755397b/Lib/httplib.py#l1144
    and `ssl.wrap_socket()`
    '''

    def __init__(self, host, **kwargs):
        '''
        Initlize the HTTP Connection class

        Args:
            host: URI of host
            kwargs: Key-worded argument dictionary, check function code for details.
        '''
        self.ciphers = kwargs.pop('ciphers',None)
        self.ca_certs = kwargs.pop('ca_certs',None)
        self.ssl_version = kwargs.pop('ssl_version', SSL.TLSv1_2_METHOD)

        httplib.HTTPSConnection.__init__(self,host,**kwargs)

    def connect(self):
        '''
        Open up a socket and create a connection.
        '''
        ctx = SSL.Context(self.ssl_version)
        # Disallow legacy SSL
        ctx.set_options(SSL.OP_NO_SSLv2 | SSL.OP_NO_SSLv3)

        if self.ciphers:
            ctx.set_cipher_list(self.ciphers)

        if self.key_file:
            ctx.use_privatekey_file(self.key_file)
            ctx.use_certificate_file(self.cert_file)

        if self.ca_certs:
            logging.debug("Verifying server TLS certs with %s", self.ca_certs)
            ctx.load_verify_locations(self.ca_certs)
            ctx.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, self.verify_cb)
            
        raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
            raw_sock.settimeout(self.timeout)

        raw_sock.connect((self.host, int(self.port)))

        conn = SSL.Connection(ctx, raw_sock)
        conn.set_connect_state() # client socket
        conn.setblocking(True)
        conn.do_handshake()
        self.sock = TLS1_2SocketAdapter(conn)

    def verify_cb(self, conn, cert, errnum, depth, ok):
        logging.debug('TLS Verify: conn: %s, cert: %s, err: %s, depth: %s, OK: %s',
                conn, cert.get_subject(), errnum, depth, ok)
        return ok


class TLS1_2SocketAdapter(object):
    '''
    PyOpenSSL wrapper that implements socket.makefile().  httplib
    calls `socket.makefile()` to make the socket behave like a file
    object.  
    
    See: http://hg.python.org/releasing/2.7.3/file/7bb96963d067/Lib/httplib.py#l339

    Note that reference counting is necessary between calls to `makefile`
    and `close` since apparently `close()` can be called before other pieces
    of code call `read()`!
    '''

    def __init__(self,conn):
        # reference counter between `makefile` and `close` calls
        self._makefile_refs = 0
        # wrapped PyOpenSSL.SSL.Connection object:
        self.conn = conn

    def makefile(self, mode='r', bufsize=-1):
        '''
        See: http://hg.python.org/releasing/2.7.3/file/7bb96963d067/Lib/ssl.py#l357
        '''
        self._makefile_refs += 1
        return socket._fileobject(self, mode=mode, bufsize=bufsize, close=True)

    def fileno(self):
        return self.conn.fileno()

    def connect(self,addr):
        return self.conn.connect(addr)

    def close(self):
        '''
        See: http://hg.python.org/releasing/2.7.3/file/7bb96963d067/Lib/ssl.py#l294
        '''
        if self._makefile_refs < 1:
            # Note SSL.Connection.shutdown() does *not* take a parameter like 
            # socket.shutdown() does
            self.conn.shutdown()
            return self.conn.close()
        else:
            self._makefile_refs -= 1

    def recv(self,bufsize=-1, flags=0):
        # Note SSL.Connections.recv() does *not* accept a `flags` param
        return self.conn.recv(bufsize)

    def send(self, string, flags=0):
        # Note SSL.Connection.send() does not take a `flags` param
        return self.conn.send(string)

    def sendall(self, string, flags=0):
        # Note SSL.Connection.sendall() does not take a `flags` param
        return self.conn.sendall(string)