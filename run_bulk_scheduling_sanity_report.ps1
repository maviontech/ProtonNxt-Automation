Push-Location $PSScriptRoot
try {
    $report = 'reports/sanity/bulk_scheduling_sanity_report.html'
    New-Item -ItemType Directory -Path 'reports/sanity' -Force | Out-Null
    python -m pytest tests/sanity/test_bulk_scheduling_sanity.py --headless --html=$report --self-contained-html
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -eq 0 -or $testExitCode -eq 1) {
        python utilities/generate_standard_report.py $report
    }
} finally {
    Pop-Location
}
exit $testExitCode
