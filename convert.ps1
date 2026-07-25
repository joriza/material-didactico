<#
.SYNOPSIS
    Convertir todos los .md de una carpeta a PDF.

.DESCRIPTION
    Detecta automaticamente el motor disponible y lo usa para convertir todos los
    .md de la carpeta indicada. Orden de preferencia:
      1. pandoc + xelatex      (mejor calidad, soporte UTF-8 nativo)
      2. pandoc + wkhtmltopdf  (decente, sin LaTeX)
      3. md-to-pdf             (Node + Chromium headless)
      4. markdown-pdf          (Node, fallback)

.PARAMETER Path
    Carpeta con los .md (default: . = directorio actual).

.PARAMETER Engine
    Forzar un motor: pandoc-xelatex | pandoc-wkhtmltopdf | md-to-pdf | markdown-pdf.
    Si se omite, se autodetecta.

.PARAMETER Force
    Regenera los PDFs que ya existen (por defecto se saltan).

.EXAMPLE
    .\convert.ps1
    .\convert.ps1 -Path output
    .\convert.ps1 -Engine md-to-pdf -Force
#>
[CmdletBinding()]
param(
    [string]$Path = ".",
    [string]$Engine,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$utf8 = New-Object System.Text.UTF8Encoding $false

function Test-Command([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Get-AvailableEngine {
    if ((Test-Command pandoc) -and (Test-Command xelatex)) { return "pandoc-xelatex" }
    if ((Test-Command pandoc) -and (Test-Command wkhtmltopdf)) { return "pandoc-wkhtmltopdf" }
    if (Test-Command md-to-pdf) { return "md-to-pdf" }
    if (Test-Command markdown-pdf) { return "markdown-pdf" }
    return $null
}

function Install-Hint([string]$eng) {
    switch ($eng) {
        "pandoc-xelatex"    { "    chocolatey install pandoc tinytex" }
        "pandoc-wkhtmltopdf"{ "    chocolatey install pandoc wkhtmltopdf" }
        "md-to-pdf"         { "    npm install -g md-to-pdf" }
        "markdown-pdf"      { "    npm install -g markdown-pdf" }
    }
}

function Convert-One([string]$engine, [string]$md, [string]$pdf) {
    switch ($engine) {
        "pandoc-xelatex" {
            pandoc $md -o $pdf --pdf-engine=xelatex `
                -V mainfont="Arial" -V geometry:margin=2cm -V lang=es
        }
        "pandoc-wkhtmltopdf" {
            pandoc $md -o $pdf --pdf-engine=wkhtmltopdf `
                -V margin-top=20 -V margin-bottom=20 -V margin-left=20 -V margin-right=20
        }
        "md-to-pdf" {
            md-to-pdf $md --pdf_options "`"{`"format`":`"A4`",`"margin`":{`"top`":`"20mm`",`"bottom`":`"20mm`",`"left`":`"20mm`",`"right`":`"20mm`"}}`""
        }
        "markdown-pdf" {
            markdown-pdf $md
        }
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
$candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path (Get-Location) $Path }
if (-not (Test-Path -LiteralPath $candidate -PathType Container)) {
    Write-Host "La carpeta '$candidate' no existe (CWD: $(Get-Location))." -ForegroundColor Red
    Write-Host "Uso: .\convert.ps1 -Path <carpeta>" -ForegroundColor Yellow
    exit 1
}
$resolved = (Get-Item -LiteralPath $candidate).FullName

$engine = if ($Engine) { $Engine } else { Get-AvailableEngine }
if (-not $engine -or (-not (Test-Command pandoc) -and $engine -notlike "md-to-pdf" -and $engine -notlike "markdown-pdf")) {
    Write-Host "No hay ningun motor disponible para convertir a PDF." -ForegroundColor Red
    Write-Host "Instala uno de estos (recomendado primero):" -ForegroundColor Yellow
    Write-Host (Install-Hint "pandoc-xelatex")
    Write-Host (Install-Hint "pandoc-wkhtmltopdf")
    Write-Host (Install-Hint "md-to-pdf")
    exit 2
}

if ($Engine -and ($engine -notlike "pandoc-*" -and $engine -ne "md-to-pdf" -and $engine -ne "markdown-pdf")) {
    Write-Host "Motor invalido: $engine" -ForegroundColor Red
    Write-Host "Validos: pandoc-xelatex | pandoc-wkhtmltopdf | md-to-pdf | markdown-pdf" -ForegroundColor Yellow
    exit 2
}

$mdFiles = Get-ChildItem -LiteralPath $resolved -Filter *.md -File
if ($mdFiles.Count -eq 0) {
    Write-Host "No hay archivos .md en '$resolved'." -ForegroundColor Yellow
    exit 0
}

Write-Host "Motor: $engine" -ForegroundColor Cyan
Write-Host "Carpeta: $resolved" -ForegroundColor Cyan
Write-Host "Archivos .md: $($mdFiles.Count)" -ForegroundColor Cyan
Write-Host ""

$ok = 0; $skipped = 0; $failed = 0
foreach ($f in $mdFiles) {
    $pdf = [System.IO.Path]::ChangeExtension($f.FullName, ".pdf")
    if ((Test-Path -LiteralPath $pdf) -and -not $Force) {
        Write-Host "  [skip] $($f.Name) (ya existe, usar -Force)" -ForegroundColor DarkGray
        $skipped++
        continue
    }
    try {
        Convert-One -engine $engine -md $f.FullName -pdf $pdf | Out-Null
        # md-to-pdf / markdown-pdf dejan el PDF junto al .md; pandoc respeta -o
        if (-not (Test-Path -LiteralPath $pdf)) {
            $altPdf = [System.IO.Path]::Combine($f.DirectoryName, [System.IO.Path]::GetFileNameWithoutExtension($f.Name) + ".pdf")
            if (Test-Path -LiteralPath $altPdf) { $pdf = $altPdf }
        }
        Write-Host "  [ok]   $($f.Name) -> $(Split-Path -Leaf $pdf)" -ForegroundColor Green
        $ok++
    } catch {
        Write-Host "  [fail] $($f.Name): $($_.Exception.Message)" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host ("Listo: {0} OK, {1} saltados, {2} fallidos." -f $ok, $skipped, $failed) -ForegroundColor Cyan
if ($failed -gt 0) { exit 3 }
exit 0
