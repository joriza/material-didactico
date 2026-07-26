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

.PARAMETER Css
    Ruta a un archivo .css para aplicar estilos al PDF. Solo soportado por
    motores basados en HTML (pandoc-wkhtmltopdf, md-to-pdf, markdown-pdf).
    pandoc-xelatex lo ignora con warning (LaTeX no usa CSS).

.PARAMETER NoFooter
    Desactiva el pie de pagina con "nro / total" (solo pandoc-wkhtmltopdf).
    Por defecto esta activado y muestra "[page] / [topage]" centrado.

.PARAMETER PageSize
    Tamaño de pagina: A4 (default), Letter, Legal, A3, etc. Cualquier valor
    aceptado por el motor (--page-size de wkhtmltopdf / --papersize de pandoc).

.EXAMPLE
    .\convert.ps1
    .\convert.ps1 -Path output
    .\convert.ps1 -Engine md-to-pdf -Force
    .\convert.ps1 -Css D:\tmp\custom-markdown.css -Path output\tmp02
    .\convert.ps1 -PageSize Letter -NoFooter
#>
[CmdletBinding()]
param(
    [string]$Path = ".",
    [string]$Engine,
    [switch]$Force,
    [string]$Css,
    [switch]$NoFooter,
    [string]$PageSize = "A4"
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

function Convert-One([string]$engine, [string]$md, [string]$pdf, [string]$css, [switch]$noFooter, [string]$pageSize = "A4") {
    $cssOk = $css -and (Test-Path -LiteralPath $css)
    if ($css -and -not $cssOk) {
        Write-Host "  [warn] CSS no encontrado: $css - se omite" -ForegroundColor Yellow
    }
    # wkhtmltopdf escribe progreso a stderr; evitar que $ErrorActionPreference=Stop lo trate como error.
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        switch ($engine) {
            "pandoc-xelatex" {
                if ($cssOk) {
                    Write-Host "  [warn] pandoc-xelatex no soporta CSS (LaTeX usa su own estilo). Se omite." -ForegroundColor Yellow
                }
                if (-not $noFooter) {
                    Write-Host "  [warn] Footer automatico no soportado en pandoc-xelatex (requiere fancyhdr en un header .tex)." -ForegroundColor Yellow
                }
                # LaTeX usa 'a4paper' (sin guion) como papersize
                $latexSize = $pageSize.ToLower() -replace '[^a-z0-9]', ''
                & pandoc $md -o $pdf --pdf-engine=xelatex `
                    -V mainfont="Arial" -V geometry:margin=2cm -V lang=es -V papersize="${latexSize}paper" 2>&1 | Out-Null
            }
            "pandoc-wkhtmltopdf" {
                $cssArg = if ($cssOk) { @("-c", $css) } else { @() }
                $fileName = [System.IO.Path]::GetFileNameWithoutExtension($md)
                # Cabecera centrada con el nombre del archivo + pie con pagina/total.
                # --pdf-engine-opt pasa las opciones DIRECTAMENTE a wkhtmltopdf.
                $hfArg = @(
                    "--pdf-engine-opt=--page-size",
                    "--pdf-engine-opt=$pageSize",
                    "--pdf-engine-opt=--header-center",
                    "--pdf-engine-opt=$fileName",
                    "--pdf-engine-opt=--header-font-size",
                    "--pdf-engine-opt=8",
                    "--pdf-engine-opt=--header-spacing",
                    "--pdf-engine-opt=4",
                    "--pdf-engine-opt=--header-line"
                )
                if (-not $noFooter) {
                    $hfArg += @(
                        "--pdf-engine-opt=--footer-center",
                        "--pdf-engine-opt=[page] / [topage]",
                        "--pdf-engine-opt=--footer-font-size",
                        "--pdf-engine-opt=8",
                        "--pdf-engine-opt=--footer-spacing",
                        "--pdf-engine-opt=4",
                        "--pdf-engine-opt=--footer-line"
                    )
                }
                & pandoc $md -o $pdf --pdf-engine=wkhtmltopdf @cssArg @hfArg `
                    -V margin-top=20 -V margin-bottom=20 -V margin-left=10 -V margin-right=10 2>&1 | Out-Null
            }
            "md-to-pdf" {
                $cssArg = if ($cssOk) { @("--css", $css) } else { @() }
                & md-to-pdf $md @cssArg 2>&1 | Out-Null
                if (-not $noFooter) {
                    Write-Host "  [warn] Footer automatico no configurado para md-to-pdf (requiere --pdf_options con displayHeaderFooter)." -ForegroundColor Yellow
                }
            }
            "markdown-pdf" {
                if ($cssOk) {
                    $cfg = Join-Path $env:TEMP "markdown-pdf-$(Get-Random).json"
                    "{`"stylesheet`": `"$($css -replace '\\','\\')`"}" | Set-Content -LiteralPath $cfg -Encoding UTF8
                    & markdown-pdf --config $cfg $md 2>&1 | Out-Null
                    Remove-Item -LiteralPath $cfg -EA SilentlyContinue
                } else {
                    & markdown-pdf $md 2>&1 | Out-Null
                }
            }
        }
    } finally {
        $ErrorActionPreference = $prevEAP
    }
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
$candidate = if ([System.IO.Path]::IsPathRooted($Path)) { $Path } else { Join-Path (Get-Location) $Path }
if (-not (Test-Path -LiteralPath $candidate -PathType Container)) {
    Write-Host "La carpeta '$candidate' no existe (CWD: $(Get-Location))." -ForegroundColor Red
    Write-Host "Uso: .\convert.ps1 -Path CARPETA" -ForegroundColor Yellow
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
Write-Host "Pagina: $PageSize" -ForegroundColor Cyan
Write-Host "Archivos .md: $($mdFiles.Count)" -ForegroundColor Cyan
if ($Css) {
    if (Test-Path -LiteralPath $Css) {
        Write-Host "CSS: $Css" -ForegroundColor Cyan
    } else {
        Write-Host "CSS: $Css (NO ENCONTRADO - se omitira)" -ForegroundColor Yellow
    }
}
if ($engine -eq "pandoc-wkhtmltopdf") {
    $footerEstado = if ($NoFooter) { "desactivado" } else { "activado: '[page] / [topage]'" }
    Write-Host "Header: centrado, nombre del archivo (8pt)" -ForegroundColor Cyan
    Write-Host "Footer: $footerEstado" -ForegroundColor Cyan
    Write-Host "Margenes laterales: 10mm (top/bottom 20mm)" -ForegroundColor Cyan
}
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
        Convert-One -engine $engine -md $f.FullName -pdf $pdf -css $Css -noFooter:$NoFooter -pageSize $PageSize
        # Convert-One silencia stderr (progreso de wkhtmltopdf); verificar exitencia real.
        if (-not (Test-Path -LiteralPath $pdf)) {
            $altPdf = [System.IO.Path]::Combine($f.DirectoryName, [System.IO.Path]::GetFileNameWithoutExtension($f.Name) + ".pdf")
            if (Test-Path -LiteralPath $altPdf) { $pdf = $altPdf } else {
                throw "pandoc no genero el PDF"
            }
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
