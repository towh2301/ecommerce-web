param(
    [switch] $NoServer,
    [switch] $CreateSuperuser,
    [string] $Username,
    [string] $Email,
    [string] $Password,
    [int] $Port = 8000
)

$ErrorActionPreference = 'Stop'

function Write-Section($text) {
    Write-Host "`n=== $text ===" -ForegroundColor Cyan
}

function Ensure-Venv {
    $venvPython = Join-Path -Path ".\.venv\Scripts" -ChildPath "python.exe"
    if (-not (Test-Path $venvPython)) {
        Write-Section "Creating virtual environment (.venv)"
        & python3 -m venv .venv
    }
    return $venvPython
}

function Install-Requirements($venvPython) {
    Write-Section "Upgrading pip and installing requirements"
    & $venvPython -m pip install --upgrade pip
    if (Test-Path "requirements.txt") {
        & $venvPython -m pip install -r requirements.txt
    } else {
        Write-Warning "requirements.txt not found. Installing core packages."
        & $venvPython -m pip install "Django>=4.2,<5.0"
    }
}

function Run-Migrations($venvPython) {
    Write-Section "Applying database migrations"
    & $venvPython manage.py migrate
}

function Maybe-CreateSuperuser($venvPython) {
    if ($CreateSuperuser) {
        if (-not $Username -or -not $Password) {
            throw "When -CreateSuperuser is specified, you must also provide -Username and -Password. Optionally provide -Email."
        }
        Write-Section "Creating Django superuser (non-interactive)"
        $env:DJANGO_SUPERUSER_USERNAME = $Username
        if ($Email) { $env:DJANGO_SUPERUSER_EMAIL = $Email } else { $env:DJANGO_SUPERUSER_EMAIL = "" }
        $env:DJANGO_SUPERUSER_PASSWORD = $Password
        try {
            & $venvPython manage.py createsuperuser --noinput
            Write-Host "Superuser created or already exists."
        } catch {
            Write-Warning "createsuperuser failed (possibly user exists). Continuing. Error: $($_.Exception.Message)"
        } finally {
            Remove-Item Env:DJANGO_SUPERUSER_USERNAME -ErrorAction SilentlyContinue
            Remove-Item Env:DJANGO_SUPERUSER_EMAIL -ErrorAction SilentlyContinue
            Remove-Item Env:DJANGO_SUPERUSER_PASSWORD -ErrorAction SilentlyContinue
        }
    }
}

function Start-Server($venvPython) {
    if (-not $NoServer) {
        Write-Section "Starting Django development server on http://127.0.0.1:$Port/"
        & $venvPython manage.py runserver "127.0.0.1:$Port"
    } else {
        Write-Host "-NoServer specified. Skipping runserver."
    }
}

# Main
try {
    Write-Section "Environment check"
    $pythonVersion = & python3 --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Python launcher 'py' not found in PATH. Install Python 3.10+ and ensure 'py' is available." }
    Write-Host "Using: $pythonVersion"

    $venvPython = Ensure-Venv

    Install-Requirements -venvPython $venvPython

    Run-Migrations -venvPython $venvPython

    Maybe-CreateSuperuser -venvPython $venvPython

    Start-Server -venvPython $venvPython

} catch {
    Write-Error "Failed: $($_.Exception.Message)"
    exit 1
}