# py-http-server-test

crappy HTTP server written in python

run from within the server directory

## configuration

configuration is in `server/config.toml`

< documentation goes here >

## goals

- [x] settings hotloading
- [ ] all http methods bar connect
  - [ ] DELETE
  - [ ] GET
  - [ ] HEAD
  - [ ] OPTIONS
  - [ ] PATCH
  - [ ] POST
  - [ ] PUT
  - [ ] TRACE
- [ ] multipart ranges
- [x] compression
- [ ] https
- [ ] simple caching
- [ ] filesystem and table routing

## theory of operation?

awful block of mermaid below

```mermaid
graph TD;
    listener("check socket")
    handler("spawn handler")
    type("type")
    hash("get md5 hash of request")
    process_request_headers("process request headers")
    process_response_headers("process response headers")
    fetch("fetch body")
    fetch_partial("fetch partial body")
    fetch_partial_multi("fetch multipart body")
    fetch_meta("fetch metadata")
    compress("compress body")
    handler_send("send response & terminate connection")
    idempotent("hash in list of GET/POST requests?")
    acl("check for access")
    acl_opt("check for access")
    cache("write to cache and/or modify resources")
    listener --> handler
    handler --> listener
    handler --> hash
    hash --> process_request_headers
    process_request_headers -->|HEAD| fetch_meta
    process_request_headers -->|TRACE| fetch_meta
    process_request_headers -->|GET| type
    process_request_headers -->|PUT| idempotent
    process_request_headers -->|POST| acl
    process_request_headers -->|DELETE| acl
    process_request_headers -->|PATCH| acl
    process_request_headers -->|OPTIONS| acl_opt
    type --> fetch
    type -->|partial| fetch_partial
    type -->|multipart| fetch_partial_multi
    fetch --> compress
    fetch_meta --> process_response_headers
    fetch_partial --> compress
    fetch_partial_multi --> compress
    compress --> process_response_headers
    process_response_headers --> handler_send
    acl --> cache
    acl_opt --> process_response_headers
    cache --> process_response_headers
    idempotent -->|no| process_response_headers
    idempotent -->|yes| acl
```

internally, configuration is done by `server.py` setting the `CONFIG` global variable in each module to an object that contains all the loaded settings

