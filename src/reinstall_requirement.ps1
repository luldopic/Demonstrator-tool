# Step 1: Deactivate the virtual environment if it's currently active
if ($env:VIRTUAL_ENV) {
    deactivate
}

# Step 2: Remove the existing venv directory if it exists
$venvPath = ".\venv"

if (Test-Path $venvPath) {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force $venvPath
}

# Step 3: Create a new virtual environment
Write-Host "Creating a new virtual environment..."
python -m venv $venvPath

# Step 4: Activate the new virtual environment
Write-Host "Activating the new virtual environment..."
& "$venvPath\Scripts\Activate.ps1"

# Step 5: Install the required packages from requirements.txt
if (Test-Path ".\requirements.txt") {
    Write-Host "Installing dependencies from requirements.txt..."
    pip install --force-reinstall -r requirements.txt
} else {
    Write-Host "requirements.txt not found!"
}

Write-Host "Virtual environment setup is complete."
