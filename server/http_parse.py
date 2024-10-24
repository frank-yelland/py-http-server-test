#!/usr/bin/env python3
"""
http parsing & response
constants:
    CONFIG
    LOGGER
    STATUS_TABLE
functions:
    process_request_headers
    process_response_headers
    process_request
"""

# import mimetypes
# import pprint


CONFIG = None
LOGGER = None
STATUS_TABLE = {
    100: b"Continue",
    101: b"Switching Protocols",
    102: b"Processing",
    103: b"Early Hints",
    200: b"OK",
    201: b"Created",
    202: b"Accepted",
    203: b"Non-Authoritative Information",
    204: b"No Content",
    205: b"Reset Content",
    206: b"Partial Content",
    207: b"Multi-Status",
    208: b"Already Reported",
    218: b"This is fine (Apache Web Server)",
    226: b"IM Used",
    300: b"Multiple Choices",
    301: b"Moved Permanently",
    302: b"Found",
    303: b"See Other",
    304: b"Not Modified",
    306: b"Switch Proxy",
    307: b"Temporary Redirect",
    308: b"Resume Incomplete",
    400: b"Bad Request",
    401: b"Unauthorized",
    402: b"Payment Required",
    403: b"Forbidden",
    404: b"Not Found",
    405: b"Method Not Allowed",
    406: b"Not Acceptable",
    407: b"Proxy Authentication Required",
    408: b"Request Timeout",
    409: b"Conflict",
    410: b"Gone",
    411: b"Length Required",
    412: b"Precondition Failed",
    413: b"Request Entity Too Large",
    414: b"Request-URI Too Long",
    415: b"Unsupported Media Type",
    416: b"Requested Range Not Satisfiable",
    417: b"Expectation Failed",
    418: b"I'm a teapot",
    421: b"Misdirected Request",
    422: b"Unprocessable Entity",
    423: b"Locked",
    424: b"Failed Dependency",
    426: b"Upgrade Required",
    428: b"Precondition Required",
    429: b"Too Many Requests",
    431: b"Request Header Fields Too Large",
    440: b"Login Time-out",
    444: b"Connection Closed Without Response",
    449: b"Retry With",
    451: b"Unavailable For Legal Reasons",
    494: b"Request Header Too Large",
    495: b"SSL Certificate Error",
    496: b"SSL Certificate Required",
    499: b"Client Closed Request",
    500: b"Internal Server Error",
    501: b"Not Implemented",
    502: b"Bad Gateway",
    503: b"Service Unavailable",
    504: b"Gateway Timeout",
    505: b"HTTP Version Not Supported",
    506: b"Variant Also Negotiates",
    507: b"Insufficient Storage",
    508: b"Loop Detected",
    509: b"Bandwidth Limit Exceeded",
    510: b"Not Extended",
    511: b"Network Authentication Required",
    520: b"Unknown Error",
    521: b"Web Server Is Down",
    522: b"Connection Timed Out",
    523: b"Origin Is Unreachable",
    524: b"A Timeout Occurred",
    525: b"SSL Handshake Failed",
    526: b"Invalid SSL Certificate",
}


def process_request_headers(client: dict, content: bytes):
    """processes request headers
    Arguments:
        client: dict: client information
        content: bytes: content of request
    Returns:
        client: dict: client information"""

    # no mutation of the original
    client = client.copy()

    # http headers are terminated with a blank line and each line terminates
    # with a \r\r, therefore the header ends with \r\n\r\n
    content = content.split(b"\r\n\r\n")
    headers = content[0].decode("utf-8").split("\r\n")
    body = content[1]

    client.update({"request": {"body": body}})

    # ===- parsing start line -===
    try:
        # splitting HTTP request into the request method, requested resource
        # and http version
        method, resource, http_version = headers[0].split(" ")
        http_version = http_version.replace("HTTP/", "")
        http_version = float(http_version)
    except ValueError:
        # error 505 - http version not supported
        LOGGER.warning("mangled http header received: '%s'", headers[0])
        message = STATUS_TABLE.get(505, b"")
        client.update({"response": {"body": message,
                                    "status": 505,
                                    "type": b"text/plain",
                                    "status_message": message}})
        return client

    if http_version > 1.1:
        # error 505 - http version not supported
        LOGGER.warning("unsupported http version '%s'", str(http_version))
        message = STATUS_TABLE.get(505, b"")
        client.update({"response": {"body": message,
                                    "status": 505,
                                    "type": b"text/plain",
                                    "status_message": message}})
        return client

    # ===- parsing headers -===
    # this seems kind of hacky - should be redone properly
    header_dict = {}
    for line in headers[1:]:
        line = line.split(":", 1)
        if len(line) == 2:
            key, value = line
            if value.startswith(" "):
                value = value[1:]
            # header keys are case insensitive
            key = key.lower()
            header_dict.update({key: value})
        else:
            LOGGER.warning("cannot parse header '%s'", line)

    useragent = header_dict.get("user-agent", None)

    # updating request information

    client.update({"request": {"method": method,
                               "resource": resource,
                               "useragent": useragent,
                               "headers": header_dict,
                               "body": body}})

    return client
