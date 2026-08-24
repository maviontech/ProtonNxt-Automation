$reportPath = "reports/manage_members_report.html"

python -m pytest tests/sanity/test_manage_members_sanity.py --headless -v --tb=short --html=$reportPath --self-contained-html
exit $LASTEXITCODE
