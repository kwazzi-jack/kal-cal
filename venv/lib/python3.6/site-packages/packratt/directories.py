# -*- coding: utf-8 -*-
from appdirs import AppDirs

_dirs = AppDirs("packratt")
user_data_dir = _dirs.user_data_dir
user_cache_dir = _dirs.user_cache_dir
user_config_dir = _dirs.user_config_dir

del _dirs
