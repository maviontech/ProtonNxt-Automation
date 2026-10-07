import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path

NAMES = {
    "calendar_settings": "Calendar & MavionMeet Settings", "bulk_scheduling": "Bulk Scheduling",
    "talent_intake_matching": "Talent Intake & Matching", "recruiter_assignment_view": "Recruiter Assignment View",
    "employee_view": "Employee View", "public_submissions": "Public Submissions", "login": "Login",
    "add_member": "Add Member", "create_jd": "Create JD", "assign_jd_to_team": "Assign JD to Team",
    "create_team": "Create Team", "manage_members": "Manage Members", "view_edit_jds": "View/Edit JDs",
    "view_jd": "View JD",
}


def config_for(path):
    suite = "Smoke" if path.parent.name.casefold() == "smoke" or "smoke" in path.stem.casefold() else "Sanity"
    module = re.sub(r"_(smoke|sanity)?_?report$", "", path.stem, flags=re.I)
    docs = list((Path("tests") / suite.lower()).glob("*TESTSUITE.md"))
    tokens = set(module.upper().split("_"))
    doc = max(docs, key=lambda item: len(tokens & set(item.stem.upper().split("_"))), default=None)
    return module, suite, doc


def plain(value):
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def suite_details(path):
    if not path or not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    result = {}
    header = []
    for line in content.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0].casefold() in {"id", "test id", "case id"}:
            header = [cell.casefold() for cell in cells]
        if len(cells) >= 4 and re.fullmatch(r"[A-Z]+(?:-[A-Z]+)*-\d{3}", cells[0]):
            scenario_index = next((i for i, value in enumerate(header) if "scenario" in value), 1)
            expected_index = next((i for i, value in enumerate(header) if "expected" in value), 3)
            detail = (cells[scenario_index], cells[expected_index])
            result[cells[0]] = detail
            # Older reports may omit the suite marker contained in documentation IDs.
            result[re.sub(r"-(?:SAN|SMK)(?=-\d{3}$)", "", cells[0])] = detail
    for section in re.split(r"(?=^##\s+)", content, flags=re.M):
        heading = re.match(r"^##\s+([A-Z]+(?:-[A-Z]+)*-\d{3})\s+-\s+(.+)$", section, re.M)
        if not heading:
            continue
        expected = re.search(r"\*\*Expected Result\*\*\s*(.*?)(?=\n(?:---|##\s)|\Z)", section, re.S)
        expected_text = ""
        if expected:
            expected_text = " ".join(re.sub(r"^[-*]\s*", "", line.strip()) for line in expected.group(1).splitlines() if line.strip())
        result[heading.group(1)] = (heading.group(2).strip(), expected_text)
    return result


def case_id(test_id):
    name = test_id.split("::")[-1]
    match = re.search(r"test_([a-z]+(?:_[a-z]+)*)_(\d{3})_", name)
    return f"{match.group(1).upper().replace('_', '-')}-{match.group(2)}" if match else name.upper()


def failure(log):
    lines = [line.strip() for line in log.splitlines() if line.strip()]
    for prefix in ("E   AssertionError:", "E   "):
        for line in lines:
            if line.startswith(prefix):
                return line[len(prefix):].strip()
    return next((line for line in lines if "Exception" in line or "Error" in line), "See the source pytest report for failure details.")


def seconds(value):
    try:
        parts = [float(part) for part in value.split(":")]
        return parts[-1] + (parts[-2] * 60 if len(parts) > 1 else 0) + (parts[-3] * 3600 if len(parts) > 2 else 0)
    except (ValueError, IndexError):
        return 0


def duration(value):
    value = int(round(value)); hours, remainder = divmod(value, 3600); minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}" if hours else f"{minutes:02d}:{secs:02d}"


def generated_at(raw):
    match = re.search(r"Report generated on (\d{2}-[A-Za-z]{3}-\d{4}) at ([0-9:]{8})", raw)
    if not match:
        match = re.search(r"Generated from .*? - (\d{2}-[A-Za-z]{3}-\d{4})(?:\s+([0-9:]{8}))?", raw)
    return f"{match.group(1)} {match.group(2) or '00:00:00'}" if match else datetime.now().strftime("%d-%b-%Y %H:%M:%S")


def pytest_rows(raw, details):
    match = re.search(r'data-jsonblob="(.*?)"', raw, re.S)
    if not match:
        return None
    data = json.loads(html.unescape(match.group(1))); rows = []
    for test_id, entries in data["tests"].items():
        entry = entries[0]; cid = case_id(test_id); result = entry["result"].upper()
        fallback = re.sub(r"^test_[a-z]+(?:_[a-z]+)*_\d{3}_", "", test_id.split("::")[-1]).replace("_", " ").capitalize()
        scenario, expected = details.get(cid, (fallback, ""))
        rows.append({"id": cid, "scenario": scenario, "expected": expected, "result": result,
                     "remark": failure(entry.get("log", "")) if result in {"FAILED", "ERROR"} else "Executed successfully.",
                     "seconds": seconds(entry.get("duration", "0"))})
    return rows, None


def table_rows(raw, heading):
    table = re.search(rf"<h2>{re.escape(heading)}</h2>\s*<table>(.*?)</table>", raw, re.S | re.I)
    if not table:
        return []
    rows = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table.group(1), re.S | re.I)[1:]:
        cells = [plain(cell) for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)]
        if cells and not cells[0].startswith("No "):
            rows.append(cells)
    return rows


def legacy_rows(raw, details):
    if "Test Execution Summary" not in raw:
        raise ValueError("Unsupported report input")
    rows = []
    for heading in ("Failed Test Cases", "Passed Test Cases", "Expected Failures"):
        for cells in table_rows(raw, heading):
            cid, scenario = cells[:2]; result = cells[-1]; remark = cells[2] if len(cells) == 4 else "Executed successfully."
            scenario, expected = details.get(cid, (scenario, ""))
            rows.append({"id": cid, "scenario": scenario, "expected": expected, "result": result, "remark": remark, "seconds": 0})
    cards = {name.strip().lower(): int(value) for name, value in re.findall(r'<div class="card(?: [^"]+)?">([^<]+)<b>(\d+)</b>', raw)}
    time = re.search(r'<div class="card">Duration<b>(.*?)</b>', raw)
    summary = {"total": cards.get("total tests", len(rows)), "passed": cards.get("passed", 0), "failed": cards.get("failed", 0),
               "errors": cards.get("errors", 0), "skipped": cards.get("skipped", 0), "xfailed": cards.get("expected failures", 0),
               "duration": plain(time.group(1)) if time else "00:00"}
    return rows, summary


CSS = r'''
:root{--navy:#102a43;--navy2:#163d63;--ink:#172b3f;--muted:#66788a;--line:#dfe7ef;--bg:#f3f6f9;--green:#087a55;--green-bg:#eaf8f2;--red:#c9362b;--red-bg:#fff0ef;--amber:#a46f00;--amber-bg:#fff7e6;font-family:Inter,"Segoe UI",Arial,sans-serif;color:var(--ink)}*{box-sizing:border-box}body{margin:0;background:var(--bg)}button,input{font:inherit}.shell{max-width:1810px;margin:auto;padding:0 38px 28px}.hero{position:relative;overflow:hidden;display:grid;grid-template-columns:1fr auto;align-items:center;gap:30px;min-height:150px;padding:30px 34px;border-radius:0 0 22px 22px;color:#fff;background:linear-gradient(120deg,#0b1f33,var(--navy2));box-shadow:0 18px 40px #0b1f332b}.hero:after{content:"";position:absolute;right:-80px;top:-165px;width:420px;height:420px;border:1px solid #ffffff1c;border-radius:50%;box-shadow:0 0 0 70px #ffffff08,0 0 0 140px #ffffff06}.brand,.hero-status{position:relative;z-index:1}.brand{display:flex;align-items:center;gap:18px}.logo{display:grid;place-items:center;width:58px;height:58px;border:1px solid #ffffff38;border-radius:14px;background:#ffffff1b;font-weight:850}.eyebrow{margin:0 0 7px;color:#b9d4ed;font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase}h1{margin:0;font-size:clamp(24px,3vw,34px)}.subtitle{margin:8px 0 0;color:#d5e4f1;font-size:13px}.hero-status{min-width:230px;padding:20px;border:1px solid #ffffff29;border-radius:14px;background:#05162647}.hero-status>span{color:#b9d4ed;font-size:10px;font-weight:800;letter-spacing:.11em;text-transform:uppercase}.run-status{display:block;margin-top:8px;font-size:13px}.hero-status small{display:block;margin-top:7px;color:#c6d8e7;font-size:11px}.meta{display:grid;grid-template-columns:repeat(7,1fr);margin-top:24px;border:1px solid var(--line);border-radius:17px;background:#fff;box-shadow:0 8px 24px #0f2a4312}.meta div{min-width:0;padding:20px 21px;border-right:1px solid #e9eef3}.meta div:last-child{border:0}.label{display:block;margin-bottom:4px;color:#7a8998;font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase}.value{display:block;overflow:hidden;color:#29445e;font-size:13px;font-weight:750;text-overflow:ellipsis;white-space:nowrap}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:24px 0}.kpi{min-height:128px;padding:30px 27px;border:1px solid var(--line);border-left:5px solid #2f6288;border-radius:17px;background:#fff;box-shadow:0 8px 24px #0f2a4312}.kpi.pass{border-left-color:#0b9b61}.kpi.fail{border-left-color:#df3027}.kpi.other{border-left-color:#d99a00}.kpi span{color:var(--muted);font-size:12px;font-weight:700}.kpi strong{display:block;margin-top:17px;color:var(--navy);font-size:32px}.kpi.pass strong{color:var(--green)}.kpi.fail strong{color:var(--red)}.kpi.other strong{color:var(--amber)}.panel{border:1px solid var(--line);border-radius:17px;background:#fff;box-shadow:0 8px 24px #0f2a4312}.overview{display:grid;grid-template-columns:320px 1fr;align-items:center;gap:26px;min-height:302px;padding:34px 38px}.donut-wrap{display:grid;place-items:center}.donut{position:relative;display:grid;place-items:center;width:210px;height:210px;border-radius:50%}.donut:before{content:"";position:absolute;width:146px;height:146px;border:1px solid #dce6ed;border-radius:50%;background:#fff}.donut-center{position:relative;z-index:1;text-align:center}.donut-center strong{display:block;color:#10375e;font-size:30px}.donut-center span{display:block;margin-top:8px;color:#5d6783;font-size:11px;font-weight:800;text-transform:uppercase}.overview h2{margin:0;color:#10375e;font-size:20px}.overview p{color:#68758f;font-size:12px}.legend{display:flex;gap:25px;margin:22px 0}.legend span{color:#46566d;font-size:11px}.dot{display:inline-block;width:8px;height:8px;margin-right:7px;border-radius:50%}.dot.pass{background:var(--green)}.dot.fail{background:var(--red)}.dot.other{background:var(--amber)}.release{padding:15px 17px;border:1px solid;border-radius:10px;font-size:11px}.release strong{display:block;margin-bottom:4px}.release.fail{border-color:#ffd8d4;background:#fff7f6;color:#961d15}.release.other{border-color:#f2d28d;background:var(--amber-bg);color:#825900}.release.pass{border-color:#b9e5d4;background:var(--green-bg);color:var(--green)}.results-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:22px;margin:30px 0 12px}.results-heading h2{margin:0;color:#10375e;font-size:20px}.results-heading p{margin:5px 0 0;color:#68758f;font-size:11px}.tools{display:flex;gap:8px;flex-wrap:wrap}.button{height:44px;padding:0 17px;border:0;border-radius:9px;background:var(--navy2);color:#fff;font-size:11px;font-weight:750;cursor:pointer}.button.secondary{background:#e7eef5;color:#123d63}.results{overflow:hidden}.table-wrap{overflow:auto}table{width:100%;min-width:1120px;border-collapse:collapse}th{position:sticky;top:0;z-index:2;padding:14px;background:#123f68;color:#fff;font-size:9px;letter-spacing:.065em;text-align:left;text-transform:uppercase}td{padding:13px 14px;border-bottom:1px solid #edf1f4;color:#394f63;font-size:11px;vertical-align:top}tbody tr:hover{background:#f8fafc}.row-fail{background:#fffafa}.case-id{color:var(--navy2)}.scenario{color:#263e54;font-weight:750}.status-pill{display:inline-flex;padding:5px 8px;border-radius:99px;font-size:9px;font-weight:850}.status-pass{background:var(--green-bg);color:var(--green)}.status-fail{background:var(--red-bg);color:#b12f26}.status-other{background:var(--amber-bg);color:var(--amber)}.defect{width:145px;padding:7px 8px;border:1px solid #d3dee7;border-radius:6px;color:#294158;font-size:10px}.remark{max-width:430px;margin-top:6px;color:#718191;font-size:9px}.footer{display:flex;justify-content:space-between;margin-top:20px;padding:14px 2px;border-top:1px solid #dbe3ea;color:#7e8c99;font-size:9px}.toast{position:fixed;right:24px;bottom:24px;padding:11px 15px;border-radius:8px;background:var(--navy);color:#fff;opacity:0;transition:.2s;pointer-events:none}.toast.show{opacity:1}@media(max-width:1050px){.meta{grid-template-columns:repeat(4,1fr)}.overview{grid-template-columns:1fr}}@media(max-width:720px){.shell{padding:0 14px 20px}.hero{grid-template-columns:1fr}.meta{grid-template-columns:repeat(2,1fr)}.kpis{grid-template-columns:repeat(2,1fr)}.results-heading{align-items:flex-start;flex-direction:column}}@media(max-width:480px){.kpis{grid-template-columns:1fr}}@media print{@page{size:landscape;margin:10mm}body{background:#fff}.shell{max-width:none;padding:0}.hero,.panel,.kpi,.meta{box-shadow:none}.hero:after,.tools,.toast{display:none}table{min-width:0}th,td{padding:7px;font-size:8px}}
'''


def render(name, module, suite, created, rows, saved=None):
    calc = {"total": len(rows), "passed": sum(r["result"] == "PASSED" for r in rows), "failed": sum(r["result"] == "FAILED" for r in rows),
            "errors": sum(r["result"] == "ERROR" for r in rows), "skipped": sum(r["result"] == "SKIPPED" for r in rows),
            "xfailed": sum(r["result"] == "XFAILED" for r in rows), "duration": duration(sum(r["seconds"] for r in rows))}
    summary = {**calc, **(saved or {})}; total = summary["total"]; passed = summary["passed"]
    bad = summary["failed"] + summary["errors"]; other = summary["skipped"] + summary["xfailed"]; rate = passed / total * 100 if total else 0
    state = "fail" if bad else "other" if other else "pass"
    title = "Completed with failures" if bad else "Execution incomplete" if other else "Quality gate passed"
    note = f"{bad} failed/error check(s) require review before sign-off." if bad else f"{other} check(s) are skipped or expected failures." if other else "All automated checks completed successfully."
    date = created.split()[0]; run_id = f"ATS-{module.replace('_','-').upper()}-{suite.upper()}-{re.sub('[^0-9A-Za-z]','',date).upper()}"
    stop = rate + (bad / total * 100 if total else 0)
    body = []
    for row in rows:
        cls = "pass" if row["result"] == "PASSED" else "fail" if row["result"] in {"FAILED", "ERROR"} else "other"
        defect = row["id"] if cls == "fail" else ""
        expected = row["expected"] or "Complete the scenario successfully without an application error."
        body.append(f'<tr class="row-{cls}"><td><strong class="case-id">{html.escape(row["id"])}</strong></td><td><span class="scenario">{html.escape(row["scenario"])}</span></td><td>{html.escape(expected)}</td><td><span class="status-pill status-{cls}">{html.escape(row["result"])}</span></td><td><input class="defect" value="{html.escape(defect)}" aria-label="Defect reference"><div class="remark">{html.escape(row["remark"])}</div></td></tr>')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(name)} {suite} | QA Automation Report</title><style>{CSS}.donut{{background:conic-gradient(#079957 0 {rate:.2f}%,#df3027 {rate:.2f}% {stop:.2f}%,#d99a00 0)}}</style></head><body><main class="shell">
<header class="hero"><div class="brand"><div class="logo">PN</div><div><p class="eyebrow">Quality Engineering · Automation Report</p><h1>{html.escape(name)} {suite} Suite</h1><p class="subtitle">ProtonNxt Applicant Tracking System</p></div></div><div class="hero-status"><span>Execution status</span><strong class="run-status">{title}</strong><small>{html.escape(note)}</small></div></header>
<section class="meta"><div><span class="label">Suite</span><span class="value">{suite}</span></div><div><span class="label">Environment</span><span class="value">Test</span></div><div><span class="label">Browser</span><span class="value">Chrome</span></div><div><span class="label">Framework</span><span class="value">Pytest + Selenium</span></div><div><span class="label">Run ID</span><span class="value">{run_id}</span></div><div><span class="label">Execution Date</span><span class="value">{date}</span></div><div><span class="label">Duration</span><span class="value">{summary["duration"]}</span></div></section>
<section class="kpis"><article class="kpi"><span>Total checks</span><strong>{total}</strong></article><article class="kpi pass"><span>Passed</span><strong>{passed}</strong></article><article class="kpi fail"><span>Failed / errors</span><strong>{bad}</strong></article><article class="kpi other"><span>Skipped / expected failures</span><strong>{other}</strong></article></section>
<section class="overview panel"><div class="donut-wrap"><div class="donut"><div class="donut-center"><strong>{rate:.1f}%</strong><span>Pass rate</span></div></div></div><div><h2>Execution overview</h2><p>Automated result distribution for this {suite.lower()}-suite run.</p><div class="legend"><span><i class="dot pass"></i>Passed <strong>{passed}</strong></span><span><i class="dot fail"></i>Failed / errors <strong>{bad}</strong></span><span><i class="dot other"></i>Other <strong>{other}</strong></span></div><div class="release {state}"><strong>{title}</strong><span>{html.escape(note)}</span></div></div></section>
<div class="results-heading"><div><h2>Detailed test results</h2><p>Outcomes are read-only. Defect IDs can be edited and saved in this browser.</p></div><div class="tools"><button class="button" id="save">Save defect IDs</button><button class="button secondary" id="csv">Export CSV</button><button class="button secondary" id="print">Print / PDF</button></div></div><section class="panel results"><div class="table-wrap"><table><thead><tr><th>Case ID</th><th>Test scenario</th><th>Expected result</th><th>Outcome</th><th>Defect reference and execution remarks</th></tr></thead><tbody>{''.join(body)}</tbody></table></div></section>
<footer class="footer"><span>ProtonNxt ATS · Quality Engineering · {html.escape(name)} {suite}</span><span>Generated {html.escape(created)} · Confidential · Internal use only</span></footer></main><div class="toast" id="toast"></div><script>
const key={json.dumps('protonnxt-report-defects-'+module+'-'+suite.lower())},inputs=[...document.querySelectorAll('.defect')];try{{const saved=JSON.parse(localStorage.getItem(key));if(Array.isArray(saved))inputs.forEach((e,i)=>{{if(saved[i]!==undefined)e.value=saved[i]}})}}catch{{}}let timer;function toast(m){{const e=document.getElementById('toast');e.textContent=m;e.classList.add('show');clearTimeout(timer);timer=setTimeout(()=>e.classList.remove('show'),2000)}}document.getElementById('save').onclick=()=>{{localStorage.setItem(key,JSON.stringify(inputs.map(e=>e.value)));toast('Defect references saved.')}};document.getElementById('print').onclick=()=>print();document.getElementById('csv').onclick=()=>{{const q=v=>'"'+String(v).replaceAll('"','""')+'"',lines=[['Case ID','Scenario','Expected Result','Outcome','Defect Reference','Remarks']];document.querySelectorAll('tbody tr').forEach(r=>{{const c=r.querySelectorAll('td');lines.push([c[0].innerText,c[1].innerText,c[2].innerText,c[3].innerText,c[4].querySelector('input').value,c[4].querySelector('.remark').innerText])}});const b=new Blob(['\\ufeff'+lines.map(r=>r.map(q).join(',')).join('\\r\\n')],{{type:'text/csv'}}),a=document.createElement('a');a.href=URL.createObjectURL(b);a.download={json.dumps(module+'_'+suite.lower()+'_results.csv')};a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);toast('CSV results exported.')}};</script></body></html>'''


def convert_report(path):
    module, suite, doc = config_for(path); raw = path.read_text(encoding="utf-8"); details = suite_details(doc)
    rows, summary = pytest_rows(raw, details) or legacy_rows(raw, details)
    path.write_text(render(NAMES.get(module, module.replace("_", " ").title()), module, suite, generated_at(raw), rows, summary), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Create professional ProtonNxt QA reports from pytest-html or legacy reports.")
    parser.add_argument("reports", nargs="+"); args = parser.parse_args()
    for item in args.reports:
        path = Path(item); convert_report(path); print(f"Converted {path}")


if __name__ == "__main__":
    main()
