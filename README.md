# py-http-server-test

crappy HTTP server written in python

## configuration

configuration is in `server/config.toml`

< documentation goes here >

## goals

- [ ] PUT, POST, GET & HEAD requests
- [ ] multipart ranges
- [ ] compression
- [ ] https
- [ ] simple caching
- [ ] filesystem and table routing

## theory of operation?

awful block of mermaid below

```mermaid
graph TD;
    listener("check socket")
    handler("spawn handler")
    process_request("type")
    hash("get md5 hash of request")
    process_request_headers("process request headers")
    process_response_headers("process response headers")
    fetch("fetch body")
    fetch_partial("fetch partial body")
    fetch_partial_multi("fetch multipart body")
    compress("compress body")
    handler_send("send response & terminate connection")
    idempotent("hash in list of GET/POST requests")
    cache("write to cache and/or modify resources")
    listener --> handler
    handler --> listener
    handler --> process_request
    process_request -->|HEAD| process_response_headers
    process_request -->|GET| process_request_headers
    process_request -->|PUT| hash
    process_request -->|POST| hash
    process_request_headers --> fetch
    process_request_headers -->|partial| fetch_partial
    process_request_headers -->|multipart| fetch_partial_multi
    fetch --> compress
    fetch_partial --> compress
    fetch_partial_multi --> compress
    compress --> process_response_headers
    process_response_headers --> handler_send
    hash --> |idempotent|idempotent
    hash --> cache
    cache --> process_response_headers
    idempotent -->|no| process_response_headers
    idempotent -->|yes| cache 
```
