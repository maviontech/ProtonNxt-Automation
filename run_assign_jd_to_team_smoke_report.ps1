$smokeReport = "reports/assign_jd_to_team_smoke_report.html"

Write-Host "Running Assign JD to Team smoke suite..."
python -m pytest tests/smoke/test_assign_jd_to_team_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE

if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}

exit $smokePytestExitCode
