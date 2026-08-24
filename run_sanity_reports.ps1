$loginReport = "reports/login_report.html"
$addMemberReport = "reports/add_member_report.html"
$manageMembersReport = "reports/manage_members_report.html"

python -m pytest tests/sanity/test_login_sanity.py --headless -v --tb=short --html=$loginReport --self-contained-html
$loginExitCode = $LASTEXITCODE

python -m pytest tests/sanity/test_add_member_sanity.py --headless -v --tb=short --html=$addMemberReport --self-contained-html
$addMemberExitCode = $LASTEXITCODE

python -m pytest tests/sanity/test_manage_members_sanity.py --headless -v --tb=short --html=$manageMembersReport --self-contained-html
$manageMembersExitCode = $LASTEXITCODE

if ($loginExitCode -ne 0 -or $addMemberExitCode -ne 0 -or $manageMembersExitCode -ne 0) {
    exit 1
}
