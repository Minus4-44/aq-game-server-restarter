# -*- coding:utf-8 -*
"""
Description:
    Base Game Server Config
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/12/2, create file.
"""
import os
import re


def expand_env_variables(path: str):
    """
    Expand environment variables in the given path.

    :param path: The path to expand.
    :return: The expanded path.
    """
    pattern = re.compile(r"\$env:([A-Za-z_][A-Za-z0-9_]*)")
    expanded_path = pattern.sub(
        lambda match: os.environ.get(match.group(1), match.group(0)), path
    )
    return expanded_path


class GameServerConfig:
    def __init__(self, game_name: str, game_server_path: str):
        """
        Base Game Server Config
        :param game_name: The name of the game
        :param game_server_path: The path of the game server
        """
        super().__init__()
        self.game_name = game_name
        self.game_server_path = game_server_path
