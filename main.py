# -*- coding:utf-8 -*
"""
Description:
    Our game server management web api
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/11/30, create file.
"""
import subprocess
from pathlib import Path

from classy_config import register_config
from fastapi import FastAPI, UploadFile
from starlette.responses import FileResponse

from config.project_zomboid.project_zomboid_config import ProjectZomboidConfig

app = FastAPI()
register_config(filepath="./config/common_config.toml", prefix="project_zomboid")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/project_zomboid/restart")
async def restart_project_zomboid_server(force_delete_saves: bool = False):
    """
    Restart project zomboid server
    :param force_delete_saves: whether to force delete saves
    :return: status
    """
    project_zomboid_config = ProjectZomboidConfig()
    if Path(project_zomboid_config.restart_server_script_path).is_file():
        paths_args = f"-ZomboidSavePath {project_zomboid_config.game_server_save_path} -SteamCmdPath {project_zomboid_config.steamcmd_path} -ServerStartPath {project_zomboid_config.game_server_path}"
        if force_delete_saves:
            subprocess.run(
                [
                    "pwsh.exe",
                    "-File",
                    project_zomboid_config.restart_server_script_path,
                    "-ForceDeleteSaves " + paths_args,
                ],
                check=True,
            )
        else:
            subprocess.run(
                [
                    "pwsh.exe",
                    "-File",
                    project_zomboid_config.restart_server_script_path,
                    paths_args,
                ],
                check=True,
            )
        return {"status": "success"}


@app.get("/project_zomboid/get_server_config")
async def get_server_config(server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    if Path(project_zomboid_config.get_server_ini_config_path()).is_file():
        return FileResponse(
            project_zomboid_config.get_server_ini_config_path(), media_type="text/plain"
        )
    else:
        return {"status": "fail", "message": "server config file not found"}


@app.post("/project_zomboid/override_server_config")
async def override_server_config(config: UploadFile, server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    if not Path(project_zomboid_config.get_server_ini_config_path()).parent.exists():
        Path(project_zomboid_config.get_server_ini_config_path()).parent.mkdir(
            parents=True, exist_ok=True
        )
    with open(project_zomboid_config.get_server_ini_config_path(), "wb") as f:
        f.write(await config.read())
    return {"status": "success"}


@app.get("/project_zomboid/get_sandbox_config")
async def get_sandbox_config(server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    if Path(project_zomboid_config.get_server_sandbox_vars_lua_path()).is_file():
        return FileResponse(
            project_zomboid_config.get_server_sandbox_vars_lua_path(),
            media_type="text/plain",
        )
    else:
        return {"status": "fail", "message": "sandbox config file not found"}


@app.post("/project_zomboid/override_sandbox_config")
async def override_sandbox_config(config: UploadFile, server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    if not Path(
        project_zomboid_config.get_server_sandbox_vars_lua_path()
    ).parent.exists():
        Path(project_zomboid_config.get_server_sandbox_vars_lua_path()).parent.mkdir(
            parents=True, exist_ok=True
        )
    with open(project_zomboid_config.get_server_sandbox_vars_lua_path(), "wb") as f:
        f.write(await config.read())
    return {"status": "success"}
