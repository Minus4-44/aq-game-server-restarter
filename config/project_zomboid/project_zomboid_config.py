# -*- coding:utf-8 -*-
"""
Description:
    Project Zomboid Server Configuration
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/12/2, created file.
"""
from pathlib import Path

from classy_config import register_config, ConfigValue

from config.base_config import SteamGameServerConfig, expand_env_variables

register_config(
    filepath="./config/project_zomboid/project_zomboid_config.toml",
    prefix="project_zomboid",
)


class ProjectZomboidConfig(SteamGameServerConfig):
    def __init__(self):
        """
        Project Zomboid Server Configuration
        Initializes configuration for Project Zomboid server
        """
        game_name = "project_zomboid"
        game_server_path = expand_env_variables(
            ConfigValue("project_zomboid.server_path", str)
        )
        super().__init__(game_name, game_server_path)
        self.game_server_config_path = expand_env_variables(
            ConfigValue("project_zomboid.server_config_path", str)
        )
        self.game_server_save_path = expand_env_variables(
            ConfigValue("project_zomboid.server_save_path", str)
        )
        self.server_name = ConfigValue("project_zomboid.server_name", str)
        self.restart_server_script_path = expand_env_variables(
            ConfigValue("project_zomboid.restart_server_script_path", str)
        )

    def get_server_ini_config_path(self):
        """
        Get the path to the server's INI configuration file
        :return: Path to the server's INI configuration file
        """
        return Path(self.game_server_config_path, f"{self.server_name}.ini").as_posix()

    def get_server_sandbox_vars_lua_path(self):
        """
        Get the path to the server's sandbox variables LUA file
        :return: Path to the server's sandbox variables LUA file
        """
        return Path(
            self.game_server_config_path, f"{self.server_name}_SandboxVars.lua"
        ).as_posix()
