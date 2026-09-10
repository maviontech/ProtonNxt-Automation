$sanityReport = "reports/sanity/assign_jd_to_team_report.html"
New-Item -ItemType Directory -Path 'reports/sanity' -Force | Out-Null

Write-Host "Running Assign JD to Team sanity suite..."
python -m pytest tests/sanity/test_assign_jd_to_team_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE

if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}

exit $sanityPytestExitCode
