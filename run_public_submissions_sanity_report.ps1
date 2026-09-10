Push-Location $PSScriptRoot
try {
    $report = "reports/sanity/public_submissions_sanity_report.html"
    New-Item -ItemType Directory -Path 'reports/sanity' -Force | Out-Null
    python -m pytest tests/sanity/test_public_submissions_sanity.py --headless --html=$report --self-contained-html
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -eq 0 -or $testExitCode -eq 1) {
        python utilities/generate_standard_report.py $report
        if ($LASTEXITCODE -ne 0 -and $testExitCode -eq 0) { $testExitCode = $LASTEXITCODE }
    }
} finally {
    Pop-Location
}
exit $testExitCode
