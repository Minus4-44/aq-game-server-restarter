# -*- coding:utf-8 -*
"""
Description:

Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/12/10, create file.
"""
from classy_config import register_config, ConfigValue

from config.base_config import SteamGameServerConfig, expand_env_variables

register_config(
    filepath="./config/satisfactory/satisfactory_config.toml",
    prefix="satisfactory",
)


class SatisfactoryConfig(SteamGameServerConfig):
    def __init__(self):
        game_name = "satisfactory"
        game_server_path = expand_env_variables(
            ConfigValue("satisfactory.server_path", str)
        )
        super().__init__(game_name, game_server_path)
        self.restart_server_script_path = expand_env_variables(
            ConfigValue("satisfactory.restart_server_script_path", str)
        )
