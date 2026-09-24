import json
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.config import Config
from pages.login_page import LoginPage
from pages.bulk_scheduling_page import BulkSchedulingPage, InterviewCalendarPage

options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1440,900')
driver = webdriver.Chrome(options=options)
try:
    driver.get(Config.BASE_URL)
    LoginPage(driver).login(
        company_code=Config.COMPANY_CODE,
        username=Config.USERNAME,
        password=Config.PASSWORD,
    )
    page = BulkSchedulingPage(driver).open()
    selected = page.select_jd('JD221')
    candidates = [page.candidate_details(i) for i in range(len(page.candidate_cards()))]
    records = InterviewCalendarPage(driver).interviews()
    candidate_ids = {str(candidate['id']) for candidate in candidates}
    matching = [
        {
            'interview_id': row.get('interview_id'),
            'candidate_id': row.get('candidate_id'),
            'interview_level': row.get('interview_level'),
            'meeting_status': row.get('meeting_status'),
            'scheduled_date': row.get('scheduled_date'),
        }
        for row in records
        if str(row.get('candidate_id')) in candidate_ids
    ]
    print(json.dumps({'jd': selected['value'], 'candidates': candidates, 'interviews': matching}))
    if '--cancel-known-test-interview' in sys.argv:
        target = next((row for row in matching if row['interview_id'] == 1), None)
        assert target == {
            'interview_id': 1,
            'candidate_id': 92,
            'interview_level': 'L1',
            'meeting_status': 'SCHEDULED',
            'scheduled_date': '2026-10-07T10:00:00',
        }, 'Interview #1 no longer matches the known test booking; refusing cancellation'
        driver.set_script_timeout(120)
        result = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];
            const token = (document.cookie.match(/(?:^|; )csrftoken=([^;]+)/) || [])[1] || '';
            fetch('/api/calendar/v1/interviews/1/cancel/', {
                method: 'POST', credentials: 'same-origin',
                headers: {'Content-Type': 'application/json', 'X-CSRFToken': token},
                body: JSON.stringify({reason: 'Cleanup of verified Bulk Scheduling test booking'})
            }).then(async response => ({status: response.status, data: await response.json()}))
              .then(done).catch(error => done({error: String(error)}));
            """
        )
        print(json.dumps({'cancellation_status': result.get('status'), 'error': result.get('error')}))
        assert result.get('status') == 200, 'Cancellation failed'
finally:
    driver.quit()
