# ============================
# build-docs.ps1
# ============================


# Guardar ruta actual
$ROOT = Get-Location

# ============================
# Build docs-gen
# ============================
Set-Location "$ROOT\docs\docs-gen"
mkdocs build

# ============================
# Build docs-op
# ============================
Set-Location "$ROOT\docs\docs-op"
mkdocs build

# Volver al root
Set-Location $ROOT

Write-Host ""
Write-Host "Documentación generada."
