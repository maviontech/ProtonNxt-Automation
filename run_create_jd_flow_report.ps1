$smokeReport = "reports/create_jd_smoke_report.html"
$sanityReport = "reports/create_jd_report.html"

Write-Host "Step 1/2: Running Create JD smoke suite..."
python -m pytest tests/smoke/test_create_jd_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE
if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}
$smokeExitCode = $smokePytestExitCode

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Create JD sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Create JD sanity suite..."
python -m pytest tests/sanity/test_create_jd_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE
if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}
exit $sanityPytestExitCode
