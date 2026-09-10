$sanityReport = "reports/sanity/view_jd_report.html"
New-Item -ItemType Directory -Path 'reports/sanity' -Force | Out-Null

Write-Host "Running View JD sanity suite..."
python -m pytest tests/sanity/test_view_jd_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE

if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}

exit $sanityPytestExitCode
