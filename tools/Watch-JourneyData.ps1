param(
    [string]$Source = "assets/img/journeys",
    [string]$Output = "assets/js/journeys-data.js"
)

$ErrorActionPreference = "Stop"

$sourcePath = (Resolve-Path -LiteralPath $Source).Path
$updateScript = Join-Path $PSScriptRoot "Update-JourneyData.ps1"
$script:watchSource = $Source
$script:watchOutput = $Output
$script:watchUpdateScript = $updateScript

function Update-Journeys {
    powershell -ExecutionPolicy Bypass -File $updateScript -Source $Source -Output $Output
}

Update-Journeys

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $sourcePath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$lastRun = Get-Date
$actions = @("Created", "Deleted", "Renamed", "Changed")

foreach ($action in $actions) {
    Register-ObjectEvent -InputObject $watcher -EventName $action -Action {
        $now = Get-Date
        if (($now - $script:lastRun).TotalMilliseconds -lt 750) {
            return
        }
        $script:lastRun = $now
        Start-Sleep -Milliseconds 250
        powershell -ExecutionPolicy Bypass -File $script:watchUpdateScript -Source $script:watchSource -Output $script:watchOutput
    } | Out-Null
}

Write-Host "Watching $Source for journey photo changes. Press Ctrl+C to stop."
while ($true) {
    Start-Sleep -Seconds 1
}
