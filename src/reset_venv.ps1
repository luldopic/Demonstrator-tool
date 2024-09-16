# Set the project path to the directory where the script is located
$projectPath = $PSScriptRoot
$venvPath = "$projectPath\venv"
$requirementsFile = "$projectPath\requirements.txt"

# Check if the virtual environment is activated, if so, deactivate it
if (Test-Path "$venvPath\\Scripts\\Activate.ps1") {
    if (Test-Path "$venvPath\\Scripts\\deactivate.ps1") {
        & "$venvPath\\Scripts\\deactivate.ps1"
    } else {
        Write-Host "No deactivate.ps1 script found, skipping deactivation."
    }
}

# Stop any process using the virtual environment's python.exe
$pythonProcesses = Get-Process | Where-Object { $_.Path -like "$venvPath\Scripts\python.exe" }
if ($pythonProcesses) {
    Write-Host "Stopping processes using the virtual environment's Python..."
    $pythonProcesses | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Remove the existing virtual environment if it exists
if (Test-Path $venvPath) {
    try {
        Remove-Item -Recurse -Force $venvPath
        Write-Host "Removed existing virtual environment at $venvPath"
    } catch {
        Write-Host "Failed to remove virtual environment: $_"
        Exit 1
    }
} else {
    Write-Host "No existing virtual environment found at $venvPath"
}

# Create a new virtual environment
python -m venv $venvPath
Write-Host "Created a new virtual environment at $venvPath"

# Wait for a moment to ensure the virtual environment is fully set up
Start-Sleep -Seconds 5

# Check the PowerShell execution policy and prompt if needed
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted" -or $executionPolicy -eq "AllSigned") {
    Write-Host "Execution policy is $executionPolicy. Consider running 'Set-ExecutionPolicy RemoteSigned' or using 'Bypass'."
}

# Activate the new virtual environment
if (Test-Path "$venvPath\Scripts\Activate.ps1") {
    & "$venvPath\Scripts\Activate.ps1"
    Write-Host "Activated the new virtual environment at $venvPath"
} else {
    Write-Host "Failed to activate the virtual environment. Please check the path and try manually activating."
    Exit 1
}

# Install required dependencies
if (Test-Path $requirementsFile) {
    pip install -r $requirementsFile
    Write-Host "Installed dependencies from $requirementsFile"
} else {
    Write-Host "No requirements.txt file found at $requirementsFile"
}

# Confirm the virtual environment reset is complete
Write-Host "Virtual environment has been reset and dependencies have been installed."
