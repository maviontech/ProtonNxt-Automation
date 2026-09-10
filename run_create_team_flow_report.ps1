$smokeReport = "reports/smoke/create_team_smoke_report.html"
New-Item -ItemType Directory -Path 'reports/smoke' -Force | Out-Null
$sanityReport = "reports/sanity/create_team_report.html"
New-Item -ItemType Directory -Path 'reports/sanity' -Force | Out-Null

Write-Host "Step 1/2: Running Create Team smoke suite..."
python -m pytest tests/smoke/test_create_team_smoke.py --headless -v --tb=short --html=$smokeReport --self-contained-html
$smokePytestExitCode = $LASTEXITCODE
if ($smokePytestExitCode -eq 0 -or $smokePytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $smokeReport
}
$smokeExitCode = $smokePytestExitCode

if ($smokeExitCode -ne 0) {
    Write-Host "Smoke suite failed. Skipping Create Team sanity suite."
    exit $smokeExitCode
}

Write-Host "Step 2/2: Smoke passed. Running Create Team sanity suite..."
python -m pytest tests/sanity/test_create_team_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE
if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}
exit $sanityPytestExitCode
