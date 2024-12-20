# -*- coding:utf-8 -*-
"""
Description:
    Game server management web API
Author:
    Fumeze(dev.fumeze@outlook.com)
History:
    2024/11/30, create file.
"""
import subprocess
from pathlib import Path
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse

from config.project_zomboid.project_zomboid_config import ProjectZomboidConfig
from config.satisfactory.satisfactory_config import SatisfactoryConfig

app = FastAPI()

# Add static files support
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request):
    """
    Render the main page
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{game_type}")
async def read_game(request: Request, game_type: str):
    """
    Render the game-specific page
    :param request: FastAPI request object
    :param game_type: Type of game server to manage
    """
    if game_type not in ["project_zomboid", "satisfactory", "palworld"]:
        return JSONResponse({"status": "fail", "message": "Unsupported game type"})
    return templates.TemplateResponse("index.html", {"request": request})


async def stream_command_output(process) -> AsyncGenerator[str, None]:
    """
    Stream command output from a subprocess
    :param process: Subprocess to stream output from
    :return: AsyncGenerator yielding output lines
    """
    try:
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            try:
                yield line.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    yield line.decode('gbk')
                except UnicodeDecodeError:
                    yield f"[Decode Error] {line}\n"
    except Exception as e:
        yield f"[Error] {str(e)}\n"
    finally:
        # Ensure process is terminated
        if process.returncode is None:
            try:
                process.kill()
            except:
                pass
        await process.wait()


@app.post("/project_zomboid/restart", tags=["project_zomboid"])
async def restart_project_zomboid_server(force_delete_saves: bool = False):
    """
    Restart Project Zomboid server
    :param force_delete_saves: Whether to force delete saves before restart
    :return: Streaming response with command output
    """
    project_zomboid_config = ProjectZomboidConfig()
    if Path(project_zomboid_config.restart_server_script_path).is_file():
        paths_args = f"-ZomboidSavePath {project_zomboid_config.game_server_save_path} -SteamCmdPath {project_zomboid_config.steamcmd_path} -ServerStartPath {project_zomboid_config.game_server_path}"
        cmd = ["pwsh.exe", "-File", project_zomboid_config.restart_server_script_path]
        if force_delete_saves:
            cmd.append("-ForceDeleteSaves " + paths_args)
        else:
            cmd.append(paths_args)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        return StreamingResponse(
            stream_command_output(process),
            media_type='text/plain'
        )
    else:
        return JSONResponse({"status": "fail", "message": "Restart script not found"})


@app.get("/project_zomboid/get_server_config", tags=["project_zomboid"])
async def get_server_config(server_name: str = ""):
    """
    Get Project Zomboid server configuration
    :param server_name: Name of the server
    :return: Server configuration content
    """
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_ini_config_path()
    if Path(config_path).is_file():
        try:
            # Try UTF-8 first
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # If failed, try GBK
            with open(config_path, 'r', encoding='gbk') as f:
                content = f.read()
        return JSONResponse({"content": content})
    else:
        return JSONResponse({"status": "fail", "message": "Server config file not found"})


@app.get("/project_zomboid/get_sandbox_config", tags=["project_zomboid"])
async def get_sandbox_config(server_name: str = ""):
    """
    Get Project Zomboid sandbox configuration
    :param server_name: Name of the server
    :return: Sandbox configuration content
    """
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_sandbox_vars_lua_path()
    if Path(config_path).is_file():
        try:
            # Try UTF-8 first
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # If failed, try GBK
            with open(config_path, 'r', encoding='gbk') as f:
                content = f.read()
        return JSONResponse({"content": content})
    else:
        return JSONResponse({"status": "fail", "message": "Sandbox config file not found"})


@app.post("/project_zomboid/override_server_config", tags=["project_zomboid"])
async def override_server_config(content: dict, server_name: str = ""):
    """
    Override Project Zomboid server configuration
    :param content: New configuration content
    :param server_name: Name of the server
    :return: Status of the operation
    """
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_ini_config_path()
    if not Path(config_path).parent.exists():
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        try:
            # Try UTF-8 first
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
    """
    Override Project Zomboid sandbox configuration
    :param content: New configuration content
    :param server_name: Name of the server
    :return: Status of the operation
    """
    project_zomboid_config = ProjectZomboidConfig()
    config_path = project_zomboid_config.get_server_sandbox_vars_lua_path()
    if not Path(config_path).parent.exists():
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        try:
            # Try UTF-8 first
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
    Restart Satisfactory server
    :return: Streaming response with command output
    """
    satisfactory_config = SatisfactoryConfig()
    if Path(satisfactory_config.restart_server_script_path).is_file():
        try:
            cmd = [
                "pwsh.exe",
                "-File",
                satisfactory_config.restart_server_script_path,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            return StreamingResponse(
                stream_command_output(process),
                media_type='text/plain'
            )
        except Exception as e:
            return JSONResponse({"status": "fail", "message": f"Error executing script: {str(e)}"})
    else:
        return JSONResponse({"status": "fail", "message": "Restart script not found"})
