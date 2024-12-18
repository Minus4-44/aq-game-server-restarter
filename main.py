# -*- coding:utf-8 -*-
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

from fastapi import FastAPI, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, FileResponse

from config.project_zomboid.project_zomboid_config import ProjectZomboidConfig
from config.satisfactory.satisfactory_config import SatisfactoryConfig

app = FastAPI()

# 添加静态文件支持
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/project_zomboid/restart", tags=["project_zomboid"])
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


@app.get("/project_zomboid/get_server_config", tags=["project_zomboid"])
async def get_server_config(server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_ini_config_path()
    if Path(config_path).is_file():
        try:
            # 首先尝试UTF-8
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果失败，尝试GBK
            with open(config_path, 'r', encoding='gbk') as f:
                content = f.read()
        return JSONResponse({"content": content})
    else:
        return JSONResponse({"status": "fail", "message": "server config file not found"})


@app.get("/project_zomboid/get_sandbox_config", tags=["project_zomboid"])
async def get_sandbox_config(server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_sandbox_vars_lua_path()
    if Path(config_path).is_file():
        try:
            # 首先尝试UTF-8
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果失败，尝试GBK
            with open(config_path, 'r', encoding='gbk') as f:
                content = f.read()
        return JSONResponse({"content": content})
    else:
        return JSONResponse({"status": "fail", "message": "sandbox config file not found"})


@app.post("/project_zomboid/override_server_config", tags=["project_zomboid"])
async def override_server_config(content: dict, server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_ini_config_path()
    if not Path(config_path).parent.exists():
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        # 使用与原文件相同的编码保存
        try:
            # 首先尝试读取原文件的编码
            with open(config_path, 'r', encoding='utf-8') as f:
                f.read()
            encoding = 'utf-8'
        except UnicodeDecodeError:
            encoding = 'gbk'
        
        with open(config_path, "w", encoding=encoding) as f:
            f.write(content["content"])
        return JSONResponse({"status": "success"})
    except Exception as e:
        return JSONResponse({"status": "fail", "message": str(e)})


@app.post("/project_zomboid/override_sandbox_config", tags=["project_zomboid"])
async def override_sandbox_config(content: dict, server_name: str = ""):
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_sandbox_vars_lua_path()
    if not Path(config_path).parent.exists():
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        # 使用与原文件相同的编码保存
        try:
            # 首先尝试读取原文件的编码
            with open(config_path, 'r', encoding='utf-8') as f:
                f.read()
            encoding = 'utf-8'
        except UnicodeDecodeError:
            encoding = 'gbk'
        
        with open(config_path, "w", encoding=encoding) as f:
            f.write(content["content"])
        return JSONResponse({"status": "success"})
    except Exception as e:
        return JSONResponse({"status": "fail", "message": str(e)})


@app.post("/satisfactory/restart", tags=["satisfactory"])
async def restart_satisfactory_server():
    """
    Restart satisfactory server
    :return: status
    """
    satisfactory_config = SatisfactoryConfig()
    if Path(satisfactory_config.restart_server_script_path).is_file():
        subprocess.run(
            ["pwsh.exe", "-File", satisfactory_config.restart_server_script_path],
            check=True,
        )
        return {"status": "success"}
    else:
        return {"status": "fail", "message": "restart script not found"}
