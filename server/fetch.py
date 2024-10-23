#!/usr/bin/env python3
"""
resource fetching, caching and storing PUT/POST requests
constants:
    CONFIG
    LOGGER
functions:
    fetch
    fetch_partial
    fetch_partial_multi
    compress
objects:
    cache
        purge_all
        purge_last
        refresh
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