# Mide un punto en una ventana visible (para que salga en la grabación de pantalla)
# y devuelve el resumen en JSON.
#   .\herramientas\punto.ps1 -Exp E1 -Cond "1 m" -Valor 1 -Instr "Llavero a 1 m"
param(
    [Parameter(Mandatory)] [string]$Exp,
    [Parameter(Mandatory)] [string]$Cond,
    [string]$Valor = "",
    [string]$Instr = "",
    [double]$Segundos = 30,
    [switch]$Simular
)
$raiz = Split-Path $PSScriptRoot -Parent
$py = Join-Path $raiz ".venv\Scripts\python.exe"
$res = Join-Path $env:TEMP "ivy_punto_resultado.json"
Remove-Item $res -ErrorAction SilentlyContinue

$a = @("herramientas\evidencias.py", "medir", "--exp", $Exp, "--cond", "`"$Cond`"",
       "--segundos", $Segundos, "--resultado", "`"$res`"")
if ($Valor -ne "") { $a += @("--valor", $Valor) }
if ($Instr -ne "") { $a += @("--instr", "`"$Instr`"") }
if ($Simular) { $a += "--simular" }

$env:PYTHONIOENCODING = "utf-8"
Start-Process -FilePath $py -ArgumentList $a -WorkingDirectory $raiz -Wait -WindowStyle Normal
$json = if (Test-Path $res) { Get-Content $res -Raw -Encoding UTF8 } else { '{"error": "no hubo resultado"}' }

# Pitidos al terminar (después de medir): 2 agudos = bien, ya puedes mover el llavero;
# 4 graves = algo salió mal (error, 0 o pocas muestras, aviso del programa) y hay que revisar.
$r = $json | ConvertFrom-Json
$mal = ($null -ne $r.error) -or ($r.n_muestras -lt 30) -or ($r.avisos.Count -gt 0)
try {
    if ($mal) { 1..4 | ForEach-Object { [console]::Beep(500, 300); Start-Sleep -Milliseconds 150 } }
    else { [console]::Beep(1200, 250); Start-Sleep -Milliseconds 120; [console]::Beep(1600, 350) }
} catch {}
$json
