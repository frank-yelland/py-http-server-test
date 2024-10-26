#!/usr/bin/env python3
"""
resource fetching, caching and storing PUT/POST requests
constants:
    CONFIG
    LOGGER
    RESPONSE_CACHE
    REQUEST_CACHE
functions:
    get_resource
    get_file
    get_meta
    get_partial
    get_partial_multi
    compress
objects:
    ResponseCache
        add
        get
        purge
        purge_all
        purge_last
        refresh
    RequestCache
        add
        get
        purge
        purge_all
"""

import zlib
# import mimetypes

# following should be handled by the flags set in CONFIG
try:
    import brotli
except ImportError:
    pass
try:
    import zstd
except ImportError:
    pass

CONFIG = None
LOGGER = None
RESPONSE_CACHE = None
REQUEST_CACHE = None


class ResponseCache:
    """cache for http responses, ie files"""
    def __init__(self):
        self.responses = []


class RequestCache:
    """cache for http requests"""
    def __init__(self):
        # {
        #     "resource_name": {
        #         "permissions"
        #
        # }
        self.resources = {}


def compress(string: bytes, method: str) -> bytes:
    """compresses string into bytes stream by the compressed method
    Arguments:
        string: bytes: data to compress
        method: string: compression method: one of gz, deflate, identity, br,
                or zstd
    Returns:
        tuple:
            0:
                string: bytes: compressed data in given format
                method: string: method used"""
    match method.lower():
        case "gz":
            return (zlib.compress(string, CONFIG.gzip_compression_level,
                                  wbits=31),
                    "gz")

        case "deflate":
            return (zlib.compress(string, CONFIG.deflate_compression_level),
                    "deflate")

        case "br":
            if not CONFIG.brotli_enabled:
                LOGGER.warning("brotli compression attempted with unloaded \
module")
                return (string, "identity")
            return (brotli.compress(string, CONFIG.brotli_compression_level),
                    "br")

        case "zstd":
            if not CONFIG.zstd_enabled:
                LOGGER.warning("zstd compression attempted with unloaded \
module")
                return (string, "identity")
            return (zstd.compress(string, CONFIG.zstd_compression_level),
                    "zstd")

        case "identity":
            return (string, "identity")

        case _:
            LOGGER.warning(f"invalid compression method '{method}'")
            return (string, "identity")


def fetch(client: dict, resource_type=None):
    """get content"""
