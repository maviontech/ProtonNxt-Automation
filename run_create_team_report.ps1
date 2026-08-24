$reportPath = "reports/create_team_report.html"

python -m pytest tests/sanity/test_create_team_sanity.py --headless -v --tb=short --html=$reportPath --self-contained-html
exit $LASTEXITCODE
