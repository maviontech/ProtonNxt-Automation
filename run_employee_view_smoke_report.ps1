$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $reportDirectory = 'reports/smoke'
    New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
    $reportPath = Join-Path $reportDirectory 'employee_view_smoke_report.html'
    $pytestReportPath = Join-Path $reportDirectory 'employee_view_smoke_pytest_report.html'
    python -m pytest tests/smoke/test_employee_view_smoke.py --headless "--html=$reportPath" --self-contained-html
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -eq 0 -or $testExitCode -eq 1) {
        Copy-Item -LiteralPath $reportPath -Destination $pytestReportPath -Force
        python utilities/generate_standard_report.py $reportPath
        if ($LASTEXITCODE -ne 0) {
            throw 'Employee View standard report generation failed'
        }
    }
} finally {
    Pop-Location
}
exit $testExitCode
