# -*- coding:utf-8 -*
"""
Description:
    Project Zomboid Config
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/12/2, create file.
"""
import os
import re
from pathlib import Path

from classy_config import register_config, ConfigValue

from config.base_config import GameServerConfig

register_config(filepath="./config/project_zomboid/project_zomboid_config.toml", prefix="project_zomboid")


def expand_env_variables(path:str):
    """
    Expand environment variables in the given path.

    :param path: The path to expand.
    :return: The expanded path.
    """
    pattern = re.compile(r'\$env:([A-Za-z_][A-Za-z0-9_]*)')
    expanded_path = pattern.sub(lambda match: os.environ.get(match.group(1), match.group(0)), path)
    return expanded_path


class ProjectZomboidConfig(GameServerConfig):
    def __init__(self):
        game_name = "project_zomboid"
        game_server_path = expand_env_variables(ConfigValue("project_zomboid.server_path", str))
        super().__init__(game_name, game_server_path)
        self.game_server_config_path = expand_env_variables(ConfigValue("project_zomboid.server_config_path", str))
        self.game_server_save_path = expand_env_variables(ConfigValue("project_zomboid.server_save_path", str))
        self.server_name = ConfigValue("project_zomboid.server_name", str)
        self.restart_server_script_path = expand_env_variables(ConfigValue("project_zomboid.restart_server_script_path", str))
        self.steamcmd_path = expand_env_variables(ConfigValue("project_zomboid.steamcmd_path", str))

    def get_server_ini_config_path(self):
        return Path(self.game_server_config_path, f"{self.server_name}.ini").as_posix()

    def get_server_sandbox_vars_lua_path(self):
        return Path(self.game_server_config_path, f"{self.server_name}_SandboxVars.lua").as_posix()