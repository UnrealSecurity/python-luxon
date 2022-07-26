from __future__ import annotations
from typing import Any
from urllib.parse import urlparse, parse_qsl, unquote
import re
import json
import socket
from luxon.consts import *

# Requests with body/payload (like 'POST') must include 
# 'Content-Length' header or use 'Transfer-Encoding: chunked'. 
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding 

class Request:
    def __init__(self, socket: socket.socket) -> None:
        self.__sock = socket
        self.__method: str = None
        self.__path: str = None
        self.__query: dict[str, str] = None
        self.__version: str = None
        self.__headers: dict[str, str] = {}
        self.__groups: tuple[re.Match] = None
        self.__body: Any = None

        # Read request headers
        with self.__sock.makefile("r", buffering=BUFFER_SIZE, encoding="utf-8", newline="\n") as f:
            self.__method, self.__path, self.__version = f.readline().split(" ")

            while True:
                line = f.readline().strip()
                if line == "": break

                header, value = line.split(": ")
                self.__headers[header] = value

        # Parse and unquote path and query string
        url = urlparse(self.__path)
        self.__path = unquote(url.path)
        self.__query = dict(parse_qsl(url.query))

    @property
    def socket(self) -> socket.socket:
        """Socket associated with this request"""
        return self.__sock

    @property
    def method(self) -> str:
        """Request method"""
        return self.__method

    @property
    def path(self) -> str:
        """Request path"""
        return self.__path

    @property
    def version(self) -> str:
        """HTTP version"""
        return self.__version

    @property
    def query(self) -> dict[str, str]:
        """HTTP query string"""
        return self.__query

    @property
    def headers(self) -> dict[str, str]:
        """Request headers"""
        return self.__headers

    @property
    def groups(self) -> tuple[re.Match]:
        """Path regular expression groups"""
        return self.__groups

    @groups.setter
    def groups(self, value: tuple[re.Match]):
        self.__groups = value

    @property
    def body(self) -> Any:
        """Request body"""
        return self.__body

    def read(self, length: int = BUFFER_SIZE) -> bytes:
        """Read data from socket associated with this request. 
        The amount of bytes read can be smaller than the buffer size.

        Args:
            length (int, optional): Buffer length. Defaults to BUFFER_SIZE.

        Returns:
            bytes
        """
        return self.__sock.recv(length)