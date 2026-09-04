$sanityReport = "reports/view_jd_report.html"

Write-Host "Running View JD sanity suite..."
python -m pytest tests/sanity/test_view_jd_sanity.py --headless -v --tb=short --html=$sanityReport --self-contained-html
$sanityPytestExitCode = $LASTEXITCODE

if ($sanityPytestExitCode -eq 0 -or $sanityPytestExitCode -eq 1) {
    python utilities/generate_standard_report.py $sanityReport
}

exit $sanityPytestExitCode
