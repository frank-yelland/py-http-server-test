#!/usr/bin/env python3
"""
parsing the config file and handling defaults
"""

import os
import tomllib as toml
from hashlib import md5

# consult settings.toml for comments on this


class Settings:
    """stores settings"""
    def __init__(self):
        """initialise settings  object with default values"""
        self.md5 = None
        self.config_path = None
        self.port = 8000
        self.ip = "0.0.0.0"
        self.log_dir = "./logs/"
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
        """loads settings from the specified config path
        Arguments:
            config_path: str: path to returns a list
        of errors encoutered while loading"""
        config_path = os.path.normpath(config_path)
        self.config_path = config_path
        try:
            with open(config_path, "rb") as file:
                self.md5 = md5(file.read()).hexdigest()
                # have to respool file
                file.seek(0)
                settings = toml.load(file)
        except OSError as error:
            return [str(error),]
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

    def reload(self):
        """reloads settings, returns a list of errors encoutered
        while reloading"""
        new_md5 = self.md5
        try:
            with open(self.config_path, "rb") as file:
                new_md5 = md5(file.read()).hexdigest()
                if new_md5 != self.md5:
                    # have to respool file
                    file.seek(0)
                    settings = toml.load(file)
        except OSError as error:
            return (False, [str(error),])

        if new_md5 != self.md5:
            # following is the same as the in the load() method
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
            old_md5 = self.md5
            self.md5 = new_md5
            return (f"{old_md5} -> {new_md5}", errors)
        return (False, [])
