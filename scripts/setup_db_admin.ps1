# Run this in an ELEVATED PowerShell (Run as Administrator). It cannot be run
# by the assistant's shell -- Chocolatey installs need admin rights, and that
# shell is a standard user session by design.
#
# Installs: PostgreSQL 18 (+ PostGIS extension) and Memurai (Redis-API
# compatible, portable -- no Windows service registered) for local dev,
# matching docs/06_DATA_MODEL.md and docs/09_SETUP_GUIDE.md.
#
# After running this, come back and tell the assistant it's done so it can
# verify the PostGIS extension is actually enabled and continue with the
# SQLAlchemy models / Alembic migration.

$ErrorActionPreference = "Stop"

Write-Host "=== Installing PostgreSQL 18 ===" -ForegroundColor Cyan
choco install postgresql --params '/Password:drashti_dev_password /Port:5432' -y

# Locate the install (choco default: C:\Program Files\PostgreSQL\18)
$pgRoot = Get-ChildItem "C:\Program Files\PostgreSQL" -Directory | Select-Object -First 1
$pgBin = Join-Path $pgRoot.FullName "bin"
Write-Host "PostgreSQL installed at $($pgRoot.FullName)"

Write-Host "=== Installing PostGIS extension files ===" -ForegroundColor Cyan
# PostGIS isn't on Chocolatey for PG18 -- pull the official Windows bundle
# and drop its files into the PostgreSQL install directory (this is the
# standard non-interactive way to add PostGIS on Windows without
# Application Stack Builder's GUI).
$postgisUrl = "https://download.osgeo.org/postgis/windows/pg18/postgis-bundle-pg18x64-setup-3.5.2.exe"
$installerPath = "$env:TEMP\postgis-bundle-setup.exe"
Invoke-WebRequest -Uri $postgisUrl -OutFile $installerPath
# Silent install into the existing PostgreSQL directory
Start-Process -FilePath $installerPath -ArgumentList "/S", "/D=$($pgRoot.FullName)" -Wait

Write-Host "=== Creating drashti role/database and enabling PostGIS ===" -ForegroundColor Cyan
$env:PGPASSWORD = "drashti_dev_password"
& "$pgBin\psql.exe" -U postgres -h localhost -c "CREATE ROLE drashti WITH LOGIN PASSWORD 'drashti_dev_password';"
& "$pgBin\createdb.exe" -U postgres -h localhost -O drashti drashti
& "$pgBin\psql.exe" -U postgres -h localhost -d drashti -c "CREATE EXTENSION IF NOT EXISTS postgis;"
& "$pgBin\psql.exe" -U postgres -h localhost -d drashti -c "SELECT PostGIS_Version();"

Write-Host "=== Installing Memurai (Redis-compatible) ===" -ForegroundColor Cyan
choco install memurai-developer.portable -y

Write-Host ""
Write-Host "Done. Tell the assistant to verify with:" -ForegroundColor Green
Write-Host "  psql -U postgres -h localhost -d drashti -c 'SELECT PostGIS_Version();'"
