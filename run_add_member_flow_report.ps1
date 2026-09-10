$smokeReport = "reports/smoke/add_member_smoke_report.html"
New-Item -ItemType Directory -Path 'reports/smoke' -Force | Out-Null
$sanityReport = "reports/sanity/add_member_report.html"
New-Item -ItemType Directory -Path 'reports/sanity' -Force | Out-Null

Write-Host "Step 1/2: Running Add Member smoke suite..."
python -m pytest tests/smoke/test_add_member_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE
if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}
$smokeExitCode = $smokePytestExitCode

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Add Member sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Add Member sanity suite..."
python -m pytest tests/sanity/test_add_member_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE
if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}
exit $sanityPytestExitCode
