$smokeReport = "reports/smoke/manage_members_smoke_report.html"
New-Item -ItemType Directory -Path 'reports/smoke' -Force | Out-Null

Write-Host "Running Manage Members smoke suite..."
python -m pytest tests/smoke/test_manage_members_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE

if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}

exit $smokePytestExitCode
