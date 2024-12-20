param (
    [string]$SteamCmdPath = "$env:USERPROFILE/scoop/shims/steamcmd.exe",
    [string]$ServerStartPath = "$env:USERPROFILE/scoop/apps/steamcmd/current/steamapps/common/PalServer/PalServer.exe"
)

[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "Stopping PalServer server..."
Stop-Process -Name "PalServer" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "PalServer-Win64-Shipping-Cmd" -Force -ErrorAction SilentlyContinue

Write-Output "Updating server..."
Start-Process -FilePath $SteamCmdPath -ArgumentList "+login anonymous +app_update 2394010 validate +quit" -NoNewWindow -Wait

Write-Output "Starting PalServer server..."
Start-Process -FilePath $ServerStartPath -ArgumentList " -log -unattended"
Write-Output "Server started."
