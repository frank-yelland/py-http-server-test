#!/usr/bin/env python3
"""
resource fetching, caching and storing PUT/POST requests
constants:
    GZIP_COMPRESSION_LVL
    DEFLATE_COMPRESSION_LVL
    COMPRESSION_PRIORITY
    RESORCE_DIR
    DEFAULT_PAGE
    REQUEST_STORAGE
    CACHE_ENABLED
    FS_ROUTING
    TABLE_ROUTING
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
