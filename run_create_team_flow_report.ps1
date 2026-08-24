$smokeReport = "reports/create_team_smoke_report.html"
$sanityReport = "reports/create_team_report.html"

Write-Host "Step 1/2: Running Create Team smoke suite..."
python -m pytest tests/smoke/test_create_team_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokeExitCode = $LASTEXITCODE

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Create Team sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Create Team sanity suite..."
python -m pytest tests/sanity/test_create_team_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
exit $LASTEXITCODE
