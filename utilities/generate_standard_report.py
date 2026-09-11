import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path


REPORT_NAME_MAP = {
    "talent_intake_matching": "Talent Intake & Matching",
    "recruiter_assignment_view": "Recruiter Assignment View",
    "employee_view": "Employee View",
    "public_submissions": "Public Submissions",
    "login": "Login",
    "add_member": "Add Member",
    "create_jd": "Create JD",
    "assign_jd_to_team": "Assign JD to Team",
    "create_team": "Create Team",
    "manage_members": "Manage Members",
    "view_edit_jds": "View/Edit JDs",
    "view_jd": "View JD",
}


REPORT_CONFIG = {
    "recruiter_assignment_view_sanity_report.html": {
        "module": "recruiter_assignment_view",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/RECRUITER_ASSIGNMENT_VIEW_SANITY_TESTSUITE.md"),
    },
    "employee_view_smoke_report.html": {
        "module": "employee_view",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/EMPLOYEE_VIEW_SMOKE_TESTSUITE.md"),
    },
    "public_submissions_sanity_report.html": {
        "module": "public_submissions",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/PUBLIC_SUBMISSIONS_SANITY_TESTSUITE.md"),
    },
    "public_submissions_smoke_report.html": {
        "module": "public_submissions",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/PUBLIC_SUBMISSIONS_SMOKE_TESTSUITE.md"),
    },
    "login_report.html": {
        "module": "login",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/LOGIN_TESTSUITE.md"),
    },
    "login_smoke_report.html": {
        "module": "login",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/LOGIN_SMOKE_TESTSUITE.md"),
    },
    "add_member_report.html": {
        "module": "add_member",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/ADD_MEMBER_TESTSUITE.md"),
    },
    "add_member_smoke_report.html": {
        "module": "add_member",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/ADD_MEMBER_SMOKE_TESTSUITE.md"),
    },
    "create_team_report.html": {
        "module": "create_team",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/CREATE_TEAM_TESTSUITE.md"),
    },
    "create_team_smoke_report.html": {
        "module": "create_team",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/CREATE_TEAM_SMOKE_TESTSUITE.md"),
    },
    "create_jd_smoke_report.html": {
        "module": "create_jd",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/CREATE_JD_SMOKE_TESTSUITE.md"),
    },
    "create_jd_report.html": {
        "module": "create_jd",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/CREATE_JD_TESTSUITE.md"),
    },
    "assign_jd_to_team_report.html": {
        "module": "assign_jd_to_team",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/ASSIGN_JD_TO_TEAM_TESTSUITE.md"),
    },
    "assign_jd_to_team_smoke_report.html": {
        "module": "assign_jd_to_team",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/ASSIGN_JD_TO_TEAM_SMOKE_TESTSUITE.md"),
    },
    "manage_members_report.html": {
        "module": "manage_members",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/MANAGE_MEMBERS_TESTSUITE.md"),
    },
    "manage_members_smoke_report.html": {
        "module": "manage_members",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/MANAGE_MEMBERS_SMOKE_TESTSUITE.md"),
    },
    "view_edit_jds_smoke_report.html": {
        "module": "view_edit_jds",
        "suite_type": "Smoke",
        "suite_doc": Path("tests/smoke/VIEW_EDIT_JDS_SMOKE_TESTSUITE.md"),
    },
    "view_jd_report.html": {
        "module": "view_jd",
        "suite_type": "Sanity",
        "suite_doc": Path("tests/sanity/VIEW_JD_TESTSUITE.md"),
    },
}


def _read_text(path):
    return path.read_text(encoding="utf-8")


def _config_for_report(report_path):
    """Return explicit configuration when available, otherwise infer a standard one.

    The fallback lets new smoke/sanity modules use the shared report layout without
    requiring a code change here before their first execution.
    """
    configured = REPORT_CONFIG.get(report_path.name)
    if configured is not None:
        return configured

    stem = report_path.stem
    suite_type = "Smoke" if "smoke" in stem.casefold() else "Sanity" if "sanity" in stem.casefold() else "Test"
    module = re.sub(r"_(smoke|sanity)?_?report$", "", stem, flags=re.IGNORECASE)
    module = module or stem
    return {"module": module, "suite_type": suite_type, "suite_doc": None}


def _load_suite_scenarios(path):
    if path is None or not path.exists():
        return {}

    content = _read_text(path)
    matches = re.findall(r"^##\s+([A-Z]+(?:-[A-Z]+)*-\d{3})\s+-\s+(.+)$", content, re.MULTILINE)
    return {case_id: title.strip() for case_id, title in matches}


def _extract_report_data(report_path):
    content = _read_text(report_path)
    match = re.search(r'data-jsonblob="(.*?)"', content, re.DOTALL)
    if not match:
        raise ValueError(f"{report_path.name} does not contain pytest-html data")

    blob = html.unescape(match.group(1))
    return json.loads(blob), content


def _extract_generated_at(raw_html):
    match = re.search(r"Report generated on ([0-9]{2}-[A-Za-z]{3}-[0-9]{4}) at ([0-9:]{8})", raw_html)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return datetime.now().strftime("%d-%b-%Y %H:%M:%S")


def _case_id_from_test_id(test_id):
    name = test_id.split("::")[-1]
    match = re.search(r"test_([a-z]+(?:_[a-z]+)*)_(\d{3})_", name)
    if match:
        return f"{match.group(1).upper().replace('_', '-')}-{match.group(2)}"
    return name.upper()


def _fallback_scenario(test_id):
    name = test_id.split("::")[-1]
    name = re.sub(r"^test_[a-z]+(?:_[a-z]+)*_\d{3}_", "", name)
    return name.replace("_", " ").strip().capitalize()


def _extract_failure_message(log):
    lines = [line.strip() for line in log.splitlines() if line.strip()]

    for line in lines:
        if line.startswith("E   AssertionError:"):
            return line.replace("E   AssertionError:", "").strip()

    for line in lines:
        if line.startswith("E   ") and "AssertionError" not in line:
            return line.replace("E   ", "").strip()

    for line in lines:
        if "TimeoutException" in line or "NoSuchDriverException" in line or "WebDriverException" in line:
            return line.strip()

    return "See execution log in the source pytest report for detailed failure information."


def _extract_duration_seconds(duration_text):
    match = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2})", duration_text)
    if match:
        hours, minutes, seconds = map(int, match.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0


def _format_duration(total_seconds):
    minutes, seconds = divmod(int(total_seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def _build_rows(data, scenario_map):
    rows = []
    for test_id, entries in data["tests"].items():
        entry = entries[0]
        case_id = _case_id_from_test_id(test_id)
        scenario = scenario_map.get(case_id, _fallback_scenario(test_id))
        result = entry["result"].upper()
        duration = entry.get("duration", "00:00:00")
        log = entry.get("log", "")

        rows.append(
            {
                "case_id": case_id,
                "scenario": scenario,
                "result": result,
                "duration": duration,
                "seconds": _extract_duration_seconds(duration),
                "actual_result": _extract_failure_message(log) if result in {"FAILED", "ERROR"} else "",
                "log": log,
            }
        )
    return rows


def _render_report(module_name, suite_type, generated_at, rows):
    total = len(rows)
    passed = sum(1 for row in rows if row["result"] == "PASSED")
    failed = sum(1 for row in rows if row["result"] == "FAILED")
    skipped = sum(1 for row in rows if row["result"] == "SKIPPED")
    xfailed = sum(1 for row in rows if row["result"] == "XFAILED")
    errors = sum(1 for row in rows if row["result"] == "ERROR")
    duration = _format_duration(sum(row["seconds"] for row in rows))
    pass_rate = (passed / total * 100) if total else 0
    overall_status = "FAILED" if failed or errors else "PASSED"
    status_class = "fail" if overall_status == "FAILED" else "pass"

    if overall_status == "FAILED":
        summary_text = f"The {suite_type.lower()} suite executed successfully, but {failed + errors} out of {total} test cases failed."
    elif xfailed:
        summary_text = f"The {suite_type.lower()} suite executed successfully with {passed} passed test cases and {xfailed} expected failure."
    else:
        summary_text = f"The {suite_type.lower()} suite executed successfully and all {total} test cases passed."

    failed_rows = [row for row in rows if row["result"] in {"FAILED", "ERROR"}]
    passed_rows = [row for row in rows if row["result"] == "PASSED"]
    xfailed_rows = [row for row in rows if row["result"] == "XFAILED"]

    execution_date = generated_at.split()[0]
    title = f"{module_name} Automation Test Report"
    suite_label = f"{module_name} {suite_type}"

    failed_table = ""
    if failed_rows:
        entries = []
        for row in failed_rows:
            entries.append(
                "<tr>"
                f"<td>{html.escape(row['case_id'])}</td>"
                f"<td>{html.escape(row['scenario'])}</td>"
                f"<td>{html.escape(row['actual_result'])}</td>"
                f"<td class=\"fail\">{html.escape(row['result'])}</td>"
                "</tr>"
            )
        failed_table = "\n".join(entries)
    else:
        failed_table = (
            "<tr>"
            "<td colspan=\"4\" class=\"pass\">No failed test cases.</td>"
            "</tr>"
        )

    passed_table = ""
    if passed_rows:
        entries = []
        for row in passed_rows:
            entries.append(
                "<tr>"
                f"<td>{html.escape(row['case_id'])}</td>"
                f"<td>{html.escape(row['scenario'])}</td>"
                "<td class=\"pass\">PASSED</td>"
                "</tr>"
            )
        passed_table = "\n".join(entries)
    else:
        passed_table = (
            "<tr>"
            "<td colspan=\"3\" class=\"fail\">No passed test cases.</td>"
            "</tr>"
        )

    xfailed_table = ""
    if xfailed_rows:
        entries = []
        for row in xfailed_rows:
            entries.append(
                "<tr>"
                f"<td>{html.escape(row['case_id'])}</td>"
                f"<td>{html.escape(row['scenario'])}</td>"
                "<td>Known environment limitation</td>"
                "<td class=\"fail\">XFAILED</td>"
                "</tr>"
            )
        xfailed_table = "\n".join(entries)
    else:
        xfailed_table = "<tr><td colspan=\"4\">No expected failures.</td></tr>"

    failure_details = ""
    if failed_rows:
        blocks = []
        for row in failed_rows:
            blocks.append(
                "<div class=\"issue\">"
                f"<strong>{html.escape(row['case_id'])}:</strong> {html.escape(row['actual_result'])}"
                "</div>"
            )
        failure_details = "\n".join(blocks)
    else:
        failure_details = "<div class=\"issue issue-pass\"><strong>No failures:</strong> All test cases passed.</div>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; background: #f4f6f9; color: #222; }}
.container {{ max-width: 1100px; margin: 30px auto; background: white; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,.12); border-radius: 8px; }}
h1 {{ margin-top: 0; }}
.meta {{ color: #666; margin-bottom: 25px; }}
h2 {{ border-bottom: 2px solid #ddd; padding-bottom: 8px; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0 25px; }}
th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; vertical-align: top; }}
th {{ background: #f1f3f5; }}
.summary {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
.card {{ flex: 1; min-width: 140px; padding: 18px; border-radius: 6px; background: #f7f7f7; }}
.card b {{ display: block; font-size: 24px; margin-top: 5px; }}
.pass {{ color: #16803c; font-weight: bold; }}
.fail {{ color: #c62828; font-weight: bold; }}
.status {{ padding: 12px 18px; border-radius: 5px; display: inline-block; font-weight: bold; }}
.status.pass {{ background: #e8f5e9; color: #1b5e20; }}
.status.fail {{ background: #fdeaea; color: #b71c1c; }}
.issue {{ background: #fff8f8; border-left: 5px solid #c62828; padding: 15px; margin: 15px 0; }}
.issue-pass {{ background: #f2fbf5; border-left-color: #16803c; }}
.footer {{ margin-top: 35px; color: #666; font-size: 13px; }}
</style>
</head>
<body>
<div class="container">
<h1>{html.escape(title)}</h1>
<div class="meta">
<strong>Execution Date:</strong> {html.escape(execution_date)} &nbsp; | &nbsp;
<strong>Test Suite:</strong> {html.escape(suite_label)} &nbsp; | &nbsp;
<strong>Framework:</strong> Pytest + Selenium
</div>

<h2>Overall Status</h2>
<div class="status {status_class}">{overall_status}</div>
<p>{html.escape(summary_text)}</p>

<h2>Test Execution Summary</h2>
<div class="summary">
<div class="card">Total Tests<b>{total}</b></div>
<div class="card pass">Passed<b>{passed}</b></div>
<div class="card fail">Failed<b>{failed}</b></div>
<div class="card">Skipped<b>{skipped}</b></div>
<div class="card">Expected Failures<b>{xfailed}</b></div>
<div class="card">Errors<b>{errors}</b></div>
<div class="card">Duration<b>{html.escape(duration)}</b></div>
<div class="card">Pass Rate<b>{pass_rate:.2f}%</b></div>
</div>

<h2>Failed Test Cases</h2>
<table>
<tr><th>Test ID</th><th>Test Scenario</th><th>Actual Result</th><th>Status</th></tr>
{failed_table}
</table>

<h2>Passed Test Cases</h2>
<table>
<tr><th>Test ID</th><th>Test Scenario</th><th>Status</th></tr>
{passed_table}
</table>

<h2>Expected Failures</h2>
<table>
<tr><th>Test ID</th><th>Test Scenario</th><th>Actual Result</th><th>Status</th></tr>
{xfailed_table}
</table>

<h2>Failure Details</h2>
{failure_details}

<h2>Conclusion</h2>
<p>Out of {total} executed {suite_type.lower()} test cases, <strong class="pass">{passed} passed</strong>, <strong>{xfailed} expected failure(s)</strong>, and <strong class="fail">{failed + errors} failed</strong>, resulting in a <strong>{pass_rate:.2f}% pass rate</strong>. The {html.escape(suite_label)} suite is currently marked as <strong class="{status_class}">{overall_status}</strong>.</p>

<div class="footer">
Generated from {html.escape(suite_label)} Automation Test Execution - {html.escape(generated_at)}
</div>
</div>
</body>
</html>
"""


def convert_report(report_path):
    config = _config_for_report(report_path)

    data, raw_html = _extract_report_data(report_path)
    scenario_map = _load_suite_scenarios(config["suite_doc"])
    rows = _build_rows(data, scenario_map)
    generated_at = _extract_generated_at(raw_html)
    module_name = REPORT_NAME_MAP[config["module"]]
    rendered = _render_report(module_name, config["suite_type"], generated_at, rows)
    report_path.write_text(rendered, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Convert pytest-html reports into the standard project report format.")
    parser.add_argument("reports", nargs="+", help="One or more HTML report paths to convert")
    args = parser.parse_args()

    for report_arg in args.reports:
        report_path = Path(report_arg)
        convert_report(report_path)
        print(f"Converted {report_path}")


if __name__ == "__main__":
    main()
