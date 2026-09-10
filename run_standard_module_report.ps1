<#!
.SYNOPSIS
Runs any pytest module and converts its pytest-html output to the standard project report format.

.EXAMPLE
./run_standard_module_report.ps1 -TestPath tests/smoke/test_employee_view_smoke.py -ReportName employee_view_smoke_report.html

.EXAMPLE
./run_standard_module_report.ps1 -TestPath tests/sanity/test_new_feature_sanity.py -ReportName new_feature_sanity_report.html
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$TestPath,

    [Parameter(Mandatory = $true)]
    [string]$ReportName
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath $TestPath -PathType Leaf)) {
        throw "Test file not found: $TestPath"
    }
    if ([IO.Path]::GetFileName($ReportName) -ne $ReportName -or -not $ReportName.EndsWith('.html')) {
        throw 'ReportName must be an HTML filename only, for example feature_smoke_report.html'
    }

    $suiteFolder = if ($TestPath -match '(^|[\\/])tests[\\/]smoke[\\/]') { 'smoke' }
                   elseif ($TestPath -match '(^|[\\/])tests[\\/]sanity[\\/]') { 'sanity' }
                   else { 'other' }
    $reportDirectory = Join-Path 'reports' $suiteFolder
    New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
    $reportPath = Join-Path $reportDirectory $ReportName
    $pytestReportPath = Join-Path $reportDirectory ($ReportName -replace '\.html$', '_pytest_report.html')
    python -m pytest $TestPath --headless "--html=$reportPath" --self-contained-html
    $testExitCode = $LASTEXITCODE

    if ($testExitCode -eq 0 -or $testExitCode -eq 1) {
        Copy-Item -LiteralPath $reportPath -Destination $pytestReportPath -Force
        python utilities/generate_standard_report.py $reportPath
        if ($LASTEXITCODE -ne 0) {
            throw 'Standard report generation failed'
        }
    }
} finally {
    Pop-Location
}
exit $testExitCode
