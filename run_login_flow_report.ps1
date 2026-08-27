 $smokeReport = "reports/login_smoke_report.html"
 $sanityReport = "reports/login_report.html"

Write-Host "Step 1/2: Running Login smoke suite..."
python -m pytest tests/smoke/test_login_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE
if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}
$smokeExitCode = $smokePytestExitCode

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Login sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Login sanity suite..."
python -m pytest tests/sanity/test_login_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE
if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}
exit $sanityPytestExitCode
