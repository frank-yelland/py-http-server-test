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


CONFIG = None
LOGGER = None
STATUS_TABLE = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    218: "This is fine (Apache Web Server)",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    306: "Switch Proxy",
    307: "Temporary Redirect",
    308: "Resume Incomplete",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    421: "Misdirected Request",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    440: "Login Time-out",
    444: "Connection Closed Without Response",
    449: "Retry With",
    450: "Blocked by Windows Parental Controls",
    451: "Unavailable For Legal Reasons",
    494: "Request Header Too Large",
    495: "SSL Certificate Error",
    496: "SSL Certificate Required",
    499: "Client Closed Request",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    509: "Bandwidth Limit Exceeded",
    510: "Not Extended",
    511: "Network Authentication Required",
    520: "Unknown Error",
    521: "Web Server Is Down",
    522: "Connection Timed Out",
    523: "Origin Is Unreachable",
    524: "A Timeout Occurred",
    525: "SSL Handshake Failed",
    526: "Invalid SSL Certificate",
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

    # header_dict = {}
    # for line in headers:
    #     line = line.split(":")
    #     header_dict.update({line[0]: line[1]})


    try:
        # splitting HTTP request into the request method, requested resource
        # and http version
        method, resource, http_version = headers[0].split(" ")
    except ValueError:
        LOGGER.warning(f"mangled http header received: '{content[0]}'")
        # error 505 - http version not supported

    return client
