#!/usr/bin/env python3
"""
parsing the config file and handling defaults
"""

import tomllib as toml

# consult settings.toml for comments on this


class Settings:
    """stores settings"""
    def __init__(self):
        """initialise settings  object with default values"""
        self.port = 8000
        self.ip = "0.0.0.0"
        self.log_dir = "./server.log"
        self.max_http_header_size = 8192
        self.server_name = "frank's web server {system}/{release})"
        self.fields = []
        self.resource_dir = "./www/"
        self.default_page = "index.html"
        self.request_storage = ""
        self.cache_enabled = False
        self.fs_routing = True
        self.table_routing = False
        self.route_table = [{}]
        self.gzip_compression_level = 6
        self.deflate_compression_level = 6
        self.brotli_compression_level = 6
        self.zstd_compression_level = 6
        self.compression_priority = ["br", "gzip", "identity", "deflate"]
        self.brotli_enabled = "False"
        self.zstd_enabled = "False"

    def load(self, config_path: str = "config.toml"):
        """loads settings from the specified config path, returns a list
        of errors encoutered while loading"""
        try:
            with open(config_path, "rb") as file:
                settings = toml.load(file)
        except OSError as error:
            return (error,)
        # setting the global variables to the setting in the config file
        server_settings = settings.get("server", None)
        http_settings = settings.get("http", None)
        resource_settings = settings.get("resource", None)
        # shit code frankly
        errors = []
        for setting in [server_settings, http_settings, resource_settings]:
            if setting is not None:
                for key, value in server_settings.items():
                    # verifying key
                    if not hasattr(self, key):
                        errors.append(f"{key} is not a valid setting")
                    # verifying types
                    if not isinstance(value, type(getattr(self, key))):
                        errors.append(f"type of {key} ({value}) was \
    {type(value.__name__)}, should be {type(globals()[key.upper()]).__name__}")
                    else:
                        setattr(self, key, value)
        return errors
