from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.application.runtime import build_project_service, build_upload_service
from src.templates import generate_workbook
from src.uploads import DuplicateDatasetError, UploadParseError
from src.uploads.templates import build_alternatives_csv_template, build_json_template, build_project_csv_template

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"

@st.cache_resource
def services():
    return build_project_service(DATABASE_PATH), build_upload_service(DATABASE_PATH)

def issue_rows(prepared):
    return [{"Code": issue.code, "Path": issue.path, "Message": issue.message} for issue in prepared.validation.issues]

def render_prepared_upload(upload_service, project, prepared):
    if prepared.validation.is_valid:
        st.success("Validation passed. This canonical dataset is eligible for immutable storage.")
    else:
        st.error("Validation failed. Correct all reported issues before saving a dataset version.")
        st.dataframe(issue_rows(prepared), width="stretch", hide_index=True)
    if prepared.validation.insufficient_data_eligible:
        st.warning("The dataset remains eligible for an insufficient-data outcome. Technical evidence and human approval controls still apply.")
    with st.expander("Canonical normalized dataset"):
        st.json(prepared.canonical_data)
    if st.button("Save immutable dataset version", disabled=not prepared.validation.is_valid, width="stretch", key=f"save-{prepared.source_type}-{prepared.original_filename}"):
        try:
            saved = upload_service.save_valid_dataset(project_id=project["project_id"], prepared=prepared)
            st.success(f"Dataset version {saved['version_number']} saved.")
            st.rerun()
        except DuplicateDatasetError as error:
            st.warning(str(error))
        except ValueError as error:
            st.error(str(error))

def main():
    st.set_page_config(page_title="PVE Upload and Validation", layout="wide")
    st.title("Upload and Validate Packaging Data")
    st.caption("Guided Excel intake plus retained JSON and CSV workflows")
    st.warning("Uploaded data is not automatically approved, qualified, or production-ready. Engineering validation and human approval remain mandatory.")
    project_service, upload_service = services()
    active_project_id = st.session_state.get("active_project_id")
    if not active_project_id:
        st.info("Select an active workspace from the Project Dashboard before uploading data.")
        st.stop()
    try:
        project = project_service.get_project(str(active_project_id))
    except KeyError:
        st.session_state.pop("active_project_id", None)
        st.error("The active project no longer exists.")
        st.stop()
    if project["archived_at"] is not None:
        st.error("Archived projects are read-only and cannot receive new uploads.")
        st.stop()
    st.success(f"Active project: {project['project_code']} — {project['project_name']}")

    st.subheader("Download Input Templates")
    excel = generate_workbook(project["category"], project["objective"], project["change_type"])
    columns = st.columns(4)
    columns[0].download_button("Download category Excel template", data=excel, file_name=f"{project['category']}_pve_intake.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    columns[1].download_button("Download JSON template", data=build_json_template(project), file_name="pve_user_upload_template.json", mime="application/json", width="stretch")
    columns[2].download_button("Download project.csv", data=build_project_csv_template(project), file_name="project.csv", mime="text/csv", width="stretch")
    columns[3].download_button("Download alternatives.csv", data=build_alternatives_csv_template(), file_name="alternatives.csv", mime="text/csv", width="stretch")

    excel_tab, json_tab, csv_tab = st.tabs(["Category Excel", "Canonical JSON", "Limited CSV Templates"])
    with excel_tab:
        st.caption("Complete the guided workbook. Validation issues are shown by field and invalid uploads cannot be saved.")
        uploaded = st.file_uploader("Upload completed .xlsx workbook", type=["xlsx"], key="pve-excel-upload")
        if uploaded is not None:
            try:
                render_prepared_upload(upload_service, project, upload_service.prepare_excel(content=uploaded.getvalue(), filename=uploaded.name, project=project))
            except UploadParseError as error:
                st.error(str(error))
    with json_tab:
        uploaded = st.file_uploader("Upload one UTF-8 JSON file", type=["json"], key="pve-json-upload")
        if uploaded is not None:
            try:
                render_prepared_upload(upload_service, project, upload_service.prepare_json(content=uploaded.getvalue(), filename=uploaded.name, project=project))
            except UploadParseError as error:
                st.error(str(error))
    with csv_tab:
        st.caption("Upload exactly project.csv and alternatives.csv. Other CSV structures remain unsupported.")
        files = st.file_uploader("Upload both CSV templates", type=["csv"], accept_multiple_files=True, key="pve-csv-upload")
        if files:
            try:
                render_prepared_upload(upload_service, project, upload_service.prepare_csv(files={item.name: item.getvalue() for item in files}, project=project))
            except UploadParseError as error:
                st.error(str(error))

    st.subheader("Saved Dataset Versions")
    versions = upload_service.datasets.list_for_project(project["project_id"])
    if versions:
        st.dataframe([{"Version": item["version_number"], "Source": item["source_type"], "Original File": item["original_filename"], "Validation": item["validation_status"], "Created": item["created_at"]} for item in versions], width="stretch", hide_index=True)
    else:
        st.info("No dataset versions have been saved for this project.")
    st.info("Only validated canonical datasets are stored. Saved versions remain immutable and project-isolated.")

if __name__ == "__main__":
    main()
