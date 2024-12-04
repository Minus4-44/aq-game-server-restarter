# -*- coding:utf-8 -*
"""
Description:
    Base Game Server Config
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/12/2, create file.
"""


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