$ErrorActionPreference = 'Stop'
$methodPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $methodPython)) {
    throw 'Project environment is missing. Follow README installation instructions first.'
}
& $methodPython -m neuro_methods @args
exit $LASTEXITCODE
