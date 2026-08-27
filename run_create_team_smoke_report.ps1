$smokeReport = "reports/create_team_smoke_report.html"

Write-Host "Running Create Team smoke suite..."
python -m pytest tests/smoke/test_create_team_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE

if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}

exit $smokePytestExitCode
