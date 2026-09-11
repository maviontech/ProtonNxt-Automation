Push-Location $PSScriptRoot
try {
    $report = 'reports/smoke/talent_intake_matching_smoke_report.html'
    New-Item -ItemType Directory -Path 'reports/smoke' -Force | Out-Null
    python -m pytest tests/smoke/test_talent_intake_matching_smoke.py --headless --html=$report --self-contained-html
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -eq 0 -or $testExitCode -eq 1) {
        python utilities/generate_standard_report.py $report
    }
} finally {
    Pop-Location
}
exit $testExitCode
