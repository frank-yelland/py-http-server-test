# py-http-server-test

Crappy HTTP server written in python, designed to serve files

## configuration & use

run from within the `server` directory

configuration is in `server/config.toml`

< documentation goes here >

---

## goals

- [x] settings hotloading
- [ ] all http methods bar CONNECT and TRACE
  - [ ] DELETE
  - [ ] GET
  - [ ] HEAD
  - [ ] OPTIONS
  - [ ] PATCH
  - [ ] POST
  - [ ] PUT
- [ ] multipart ranges
- [x] compression
- [ ] cookies support
- [ ] https
- [ ] simple caching
- [ ] filesystem and table routing

---

## theory of operation

```mermaid
%%{init: {"flowchart": {"curve": "stepAfter", "defaultRenderer": "elk"}}}%% 
flowchart TD;
    init(["initialise server"])
    listener("check socket")
    handler("spawn handler")
    receive[/"read socket"/]
    type{{"fetch type"}}
    hash("get md5 hash of request")
    process_request_headers{{"process request headers"}}
    process_response_headers(["gather and process response headers"])
    fetch("fetch body")
    fetch_partial("fetch partial body")
    fetch_partial_multi("fetch multipart body")
    fetch_meta("fetch metadata")
    idempotent{{"md5 in list of PUT requests?"}}
    compress("compress body")
    handler_send[/"send response"/]
    handler_end(["terminate connection"])
    acl{{"check for access"}}
    cache(["write to cache and/or modify resources"])
    unsupported("501 not implemented or 403 forbidden")
    denied("403 forbidden")
    init --> listener
    listener --> handler
    handler --> listener
    handler --> receive
    receive --> hash
    hash --> process_request_headers
    process_request_headers -->|HEAD, GET, or OPTIONS| type
    process_request_headers -->|PUT, POST, DELETE, or PATCH| acl
    process_request_headers -->|CONNECT, TRACE, or mangled| unsupported
    type -->|full| fetch
    type -->|partial| fetch_partial
    type -->|multipart| fetch_partial_multi
    type -->|"metadata (HEAD or OPTIONS)"| fetch_meta
    acl -->|access| cache
    acl -->|access & PUT request|idempotent
    acl -->|no access|denied
    %% the arrowheads are a bug as of october 2024
    fetch --- process_response_headers
    fetch_meta --- process_response_headers
    fetch_partial --- process_response_headers
    fetch_partial_multi --- process_response_headers
    cache --- process_response_headers
    denied --- process_response_headers
    unsupported --- process_response_headers
    idempotent -->|yes| cache
    idempotent ---|no| process_response_headers
    process_response_headers --> compress
    compress --> handler_send
    handler_send --> handler_end

    classDef join height:0
```

internally, configuration is done by `server.py` setting the `CONFIG` global variable in each module to an object that contains all the loaded settings
