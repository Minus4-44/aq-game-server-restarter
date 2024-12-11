param (
    [string]$SteamCmdPath = "$env:USERPROFILE/scoop/shims/steamcmd.exe",
    [string]$ServerStartPath = "$env:USERPROFILE/scoop/apps/steamcmd/current/steamapps/common/SatisfactoryDedicatedServer/FactoryServer.exe"
)

[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Output "Stopping satisfactory server..."
Stop-Process -Name "FactoryServer" -Force -ErrorAction SilentlyContinue

Write-Output "Updating server..."
Start-Process -FilePath $SteamCmdPath -ArgumentList "+login anonymous +app_update 1690800 validate +quit" -NoNewWindow -Wait

Write-Output "Starting satisfactory server..."
Start-Process -FilePath $ServerStartPath -ArgumentList " -log -unattended"
Write-Output "Server started."
