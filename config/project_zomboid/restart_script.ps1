param (
    [switch]$ForceDeleteSaves,
    [string]$ZomboidSavePath = "$env:USERPROFILE/Zomboid/Saves/Multiplayer",
    [string]$SteamCmdPath = "$env:USERPROFILE/scoop/shims/steamcmd.exe",
    [string]$ServerStartPath = "$env:USERPROFILE/scoop/apps/steamcmd/current/steamapps/common/Project Zomboid Dedicated Server/StartServer64.bat"
)

[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "Stopping server..."
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "javaw" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "ProjectZomboid64" -Force -ErrorAction SilentlyContinue

if ($ForceDeleteSaves) {
    Write-Output "Force delete save..."
    Remove-Item -Path $ZomboidSavePath -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Output "Updating server..."
Start-Process -FilePath $SteamCmdPath -ArgumentList "+login anonymous +app_update 380870 +quit" -NoNewWindow -Wait

Write-Output "Starting server..."
Start-Process -FilePath $ServerStartPath
Write-Output "Server started."
