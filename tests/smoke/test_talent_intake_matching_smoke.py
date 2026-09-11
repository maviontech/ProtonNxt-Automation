"""Smoke coverage for SMK-TIM-001 through SMK-TIM-022.

Uploads create records in the selected test JD. Run this suite only against a
dedicated tenant and configure the optional JD/candidate queries in its data file.
"""
import json
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.talent_intake_matching_page import TalentIntakeMatchingPage


pytestmark = pytest.mark.smoke
DATA = json.loads((Path(__file__).resolve().parents[2] / 'testdata/talent_intake_matching_smoke_data.json').read_text(encoding='utf-8'))


@pytest.fixture
def page(driver, credentials):
    login = LoginPage(driver)
    login.login(**credentials)
    assert login.is_authenticated_destination_displayed(), 'Admin login failed'
    return TalentIntakeMatchingPage(driver).open()


@pytest.fixture
def selected_jd(page):
    return page.select_jd(DATA['jd_query'] or None)


@pytest.fixture
def upload_files(tmp_path):
    token = uuid4().hex[:10]
    document = tmp_path / f'tim_smoke_{token}.docx'
    # A compact DOCX archive is sufficient for the application's accepted-file validation.
    with ZipFile(document, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        archive.writestr('word/document.xml', f'<document>Talent Intake Smoke {token}</document>')
    second = tmp_path / f'tim_smoke_{token}_second.docx'
    second.write_bytes(document.read_bytes())
    unsupported = tmp_path / f'tim_smoke_{token}.txt'
    unsupported.write_text('Unsupported upload type', encoding='utf-8')
    bundle = tmp_path / f'tim_smoke_{token}.zip'
    with ZipFile(bundle, 'w') as archive:
        archive.write(document, document.name)
        archive.write(second, second.name)
    return document, second, unsupported, bundle


def _open_selected_upload(page, selected_jd):
    page.open_upload()
    assert page.is_visible(page.UPLOAD_MODAL), 'Upload dialog did not open for the selected JD'


def _processed_upload(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    page.upload_file(upload_files[0])
    page.wait.until(lambda _: page.upload_message())
    return upload_files[0]


def test_smk_tim_001_open_page(page):
    assert 'Talent Intake & Matching' in page.driver.find_element(By.TAG_NAME, 'body').text
    assert page.visible(page.JD_SEARCH)
    assert page.visible(page.UPLOAD).is_enabled() and page.visible(page.EXPORT).is_enabled()


def test_smk_tim_002_load_available_jds(page):
    options = page.open_jd_picker()
    assert options and all(option.get_attribute('data-value') for option in options)


def test_smk_tim_003_select_jd(page, selected_jd):
    label, jd_id = selected_jd
    assert jd_id and label
    assert page.visible(page.JD_SEARCH).get_attribute('value').strip()


def test_smk_tim_004_upload_without_jd(page):
    page.open_upload()
    assert page.is_visible(page.ACTION_RESULT)
    assert 'please select a jd first' in page.visible(page.ACTION_MESSAGE).text.casefold()


def test_smk_tim_005_close_jd_required_message(page):
    page.open_upload()
    page.close_action_result()
    assert not page.is_visible(page.ACTION_RESULT)
    assert page.visible(page.JD_SEARCH)


def test_smk_tim_006_open_upload_after_jd_selection(page, selected_jd):
    _open_selected_upload(page, selected_jd)
    assert selected_jd[1] in page.driver.find_element(By.ID, 'upload-jd-id').get_attribute('value')


def test_smk_tim_007_close_upload_dialog(page, selected_jd):
    _open_selected_upload(page, selected_jd)
    page.close_upload()
    assert not page.is_visible(page.UPLOAD_MODAL)


def test_smk_tim_008_upload_one_valid_resume(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    page.upload_file(upload_files[0])
    assert page.upload_message(), 'Upload did not show progress or a result message'


def test_smk_tim_009_upload_multiple_valid_resumes(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    page.driver.find_element(*page.RESUME_FILE).send_keys('\n'.join(str(path) for path in upload_files[:2]))
    page.click(page.UPLOAD_SAVE)
    page.wait.until(lambda _: page.upload_message())
    assert page.upload_message()


def test_smk_tim_010_required_file_validation(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    assert not page.visible(page.UPLOAD_SAVE).is_enabled(), 'Upload should be disabled without a file'

    # Selecting a supported file should enable upload without submitting it.
    file_input = page.driver.find_element(*page.RESUME_FILE)
    file_input.send_keys(str(upload_files[0]))
    page.wait.until(EC.element_to_be_clickable(page.UPLOAD_SAVE), 'Upload should become enabled after selecting a file')


def test_smk_tim_011_reject_unsupported_file_type(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    page.driver.find_element(*page.RESUME_FILE).send_keys(str(upload_files[2]))
    page.click(page.UPLOAD_SAVE)
    page.wait.until(lambda _: page.upload_message())
    assert any(word in page.upload_message().casefold() for word in ('unsupported', 'invalid', 'pdf', 'doc'))


def test_smk_tim_012_upload_zip_archive(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    page.choose_upload_source('ZIP Archive')
    page.upload_file(upload_files[3], zip_archive=True)
    assert page.upload_message()


def test_smk_tim_013_add_existing_candidate(page, selected_jd):
    if not DATA['existing_candidate_query']:
        pytest.skip('Set existing_candidate_query in talent_intake_matching_smoke_data.json')
    _open_selected_upload(page, selected_jd)
    page.choose_upload_source('Existing Candidate')
    field = page.visible(page.EXISTING_SEARCH)
    field.send_keys(DATA['existing_candidate_query'])
    # Wait for an actual matching result, not the initial search placeholder.
    result = page.wait.until(EC.visibility_of_element_located((
        By.CSS_SELECTOR, '#existing-candidate-results button[data-existing-candidate-id]'
    )))
    candidate_name = result.find_element(By.CSS_SELECTOR, '.upload-existing-card__name').text.strip()
    candidate_email = result.find_element(By.CSS_SELECTOR, '.upload-existing-card__meta').text.split('·')[0].strip()
    assert candidate_name, 'Search result has no candidate name'
    if not result.is_enabled():
        # Repeat runs must verify the existing attachment rather than wait for
        # an already-attached candidate to become selectable.
        assert 'already attached' in result.text.casefold(), 'Candidate is disabled for an unexpected reason'
        assert not page.visible(page.UPLOAD_SAVE).is_enabled(), 'An already-attached candidate should not enable Attach'
        print('[Existing Candidate] Already attached; verifying the candidate in the selected JD')
    else:
        page.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", result)
        result.click()
        page.click(page.UPLOAD_SAVE)
        page.wait.until(lambda _: page.upload_message())

    page.close_upload()
    page.driver.refresh()
    page.wait_ready()
    _, refreshed_jd_id = page.select_jd(selected_jd[1])
    assert refreshed_jd_id == selected_jd[1], 'Refresh selected a different JD'
    page.wait.until(
        lambda _: any(
            row.find_element(By.CSS_SELECTOR, 'td.name-col').text.strip() == candidate_name
            and (candidate_email == 'No email' or row.find_element(By.CSS_SELECTOR, 'td.email-col').text.strip() == candidate_email)
            for row in page.rows()
            if row.find_elements(By.CSS_SELECTOR, 'td.name-col')
        ),
        f'Candidate {candidate_name!r} was not found in the selected JD after refresh',
    )


def test_smk_tim_014_progress_and_activity(page, selected_jd, upload_files):
    _open_selected_upload(page, selected_jd)
    page.choose_upload_tab('Progress & Activity')
    assert page.is_visible((By.ID, 'upload-progress-shell')) or page.is_visible((By.ID, 'upload-stage-list'))


def test_smk_tim_015_parsed_resume_record(page, selected_jd, upload_files):
    _processed_upload(page, selected_jd, upload_files)
    page.close_upload()
    page.wait.until(lambda _: page.rows())
    cells = [cell.text.strip() for cell in page.rows()[0].find_elements(By.TAG_NAME, 'td')]
    assert len(cells) >= 7 and any(upload_files[0].name in cell for cell in cells)


def test_smk_tim_016_switch_to_cards(page, selected_jd, upload_files):
    _processed_upload(page, selected_jd, upload_files)
    page.close_upload()
    page.wait.until(lambda _: page.rows())
    cards = page.view_toggle('Cards')
    cards.click()
    page.wait.until(lambda _: 'active' in cards.get_attribute('class'))
    assert page.is_visible(page.CARDS)


def test_smk_tim_017_switch_to_list(page, selected_jd):
    page.view_toggle('Cards').click()
    page.view_toggle('List').click()
    page.wait.until(lambda _: page.is_visible(page.TABLE))
    assert page.is_visible(page.TABLE) and page.selected_jd_id == selected_jd[1]


def test_smk_tim_018_open_resume_action(page, selected_jd, upload_files):
    uploaded_file = _processed_upload(page, selected_jd, upload_files)
    page.close_upload()
    row = page.wait.until(
        lambda _: next((row for row in page.rows() if uploaded_file.name in row.text), False),
        'The uploaded resume did not appear in the results',
    )
    # Edit Resume opens candidate details; Parse and Delete are separate actions.
    action = row.find_element(By.CSS_SELECTOR, 'button.edit-btn[title="Edit Resume"]')
    resume_id = action.get_attribute('data-resume-id')
    assert resume_id, 'Edit Resume action has no resume ID'
    page.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", action)
    page.wait.until(EC.element_to_be_clickable(action)).click()
    page.visible((By.ID, 'candidate-modal'))
    page.wait.until(
        lambda d: d.find_element(By.ID, 'modal-resume-id').get_attribute('value') == resume_id,
        'Candidate dialog did not load the selected resume',
    )


def test_smk_tim_019_export_selected_jd_results(page, selected_jd):
    page.click(page.EXPORT)
    page.wait.until(lambda _: page.is_visible(page.ACTION_RESULT) or 'export' in page.driver.find_element(By.TAG_NAME, 'body').text.casefold())


def test_smk_tim_020_empty_result_state(page):
    if not DATA['empty_jd_query']:
        pytest.skip('Set empty_jd_query to a dedicated JD with no resumes')
    page.select_jd(DATA['empty_jd_query'])
    # A blank tbody also occurs while results are loading. Wait for the
    # completed empty response, which renders a message row in list view.
    empty_message = (By.CSS_SELECTOR, '#resumes-tbody td[colspan]')
    page.wait.until(
        EC.text_to_be_present_in_element(empty_message, 'No resumes found for the selected JD.'),
        f'No empty-results message appeared for JD {DATA["empty_jd_query"]}',
    )
    assert page.is_visible(empty_message), 'The empty-results message is hidden'
    assert not page.driver.find_elements(By.CSS_SELECTOR, '#resumes-tbody tr[data-resume-id]'), \
        'The empty JD unexpectedly contains resume records'


def test_smk_tim_021_change_selected_jd(page, selected_jd):
    if not DATA['alternate_jd_query']:
        pytest.skip('Set alternate_jd_query to a second JD')
    first_id = selected_jd[1]
    _, second_id = page.select_jd(DATA['alternate_jd_query'])
    assert second_id and second_id != first_id


def test_smk_tim_022_refresh_stable_behavior(page, selected_jd):
    page.driver.refresh()
    page.wait_ready()
    _open_selected_upload(page, page.select_jd(DATA['jd_query'] or None))
    page.close_upload()
