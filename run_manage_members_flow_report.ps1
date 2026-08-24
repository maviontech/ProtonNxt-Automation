$smokeReport = "reports/manage_members_smoke_report.html"
$sanityReport = "reports/manage_members_report.html"

Write-Host "Step 1/2: Running Manage Members smoke suite..."
python -m pytest tests/smoke/test_manage_members_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokeExitCode = $LASTEXITCODE

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Manage Members sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Manage Members sanity suite..."
python -m pytest tests/sanity/test_manage_members_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
exit $LASTEXITCODE
