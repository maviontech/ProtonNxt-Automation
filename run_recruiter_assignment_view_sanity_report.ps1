# Optional future execution entry point. Not run when the suite is created.
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $reportDirectory = 'reports/sanity'
    New-Item -ItemType Directory -Path $reportDirectory -Force | Out-Null
    $reportPath = Join-Path $reportDirectory 'recruiter_assignment_view_sanity_report.html'
    $pytestReportPath = Join-Path $reportDirectory 'recruiter_assignment_view_sanity_pytest_report.html'
    $junitPath = Join-Path $reportDirectory 'recruiter_assignment_view_sanity_results.xml'
    python -m pytest tests/sanity/test_recruiter_assignment_view_sanity.py --headless "--html=$reportPath" --self-contained-html "--junitxml=$junitPath"
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -eq 0 -or $testExitCode -eq 1) {
        Copy-Item -LiteralPath $reportPath -Destination $pytestReportPath -Force
        python utilities/generate_standard_report.py $reportPath
        if ($LASTEXITCODE -ne 0) {
            throw 'Recruiter Assignment View standard report generation failed'
        }
    }
} finally {
    Pop-Location
}
exit $testExitCode
