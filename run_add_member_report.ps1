$smokeReport = "reports/add_member_smoke_report.html"
$sanityReport = "reports/add_member_report.html"

Write-Host "Step 1/2: Running Add Member smoke suite..."
python -m pytest tests/smoke/test_add_member_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokeExitCode = $LASTEXITCODE

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Add Member sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Add Member sanity suite..."
python -m pytest tests/sanity/test_add_member_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
exit $LASTEXITCODE
