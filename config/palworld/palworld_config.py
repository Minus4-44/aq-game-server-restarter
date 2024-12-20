# -*- coding:utf-8 -*-
"""
Description:
    PalWorld Game Server Configuration
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/12/20, created file.
"""
from pathlib import Path

from classy_config import register_config, ConfigValue

from config.base_config import SteamGameServerConfig, expand_env_variables

register_config(
    filepath="./config/palworld/palworld_config.toml",
    prefix="palworld",
)


class PalWorldConfig(SteamGameServerConfig):
    def __init__(self):
        """
        PalWorld Server Configuration
        Initializes configuration for PalWorld server
        """
        game_name = "palworld"
        game_server_path = expand_env_variables(
            ConfigValue("palworld.server_path", str)
        )
        super().__init__(game_name, game_server_path)
        self.game_server_config_path = expand_env_variables(
            ConfigValue("palworld.server_config_path", str)
        )
        self.game_server_save_path = expand_env_variables(
            ConfigValue("palworld.server_save_path", str)
        )
        self.restart_server_script_path = expand_env_variables(
            ConfigValue("palworld.restart_server_script_path", str)
        )

    def get_server_ini_config_path(self):
        """
        Get the path to the server's INI configuration file
        :return: Path to the server's INI configuration file
        """
        return Path(self.game_server_config_path, f"PalWorldSettings.ini").as_posix()
