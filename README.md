# Meta Table ETL Cleaning

This tool automates the process of reading data from Source Google Sheets, cleaning/transforming it, and writing it to a Target Google Sheet.

## 🚀 Quick Start

1.  **Setup Environment** (First time only):
    Double-click `setup_env.bat`. This will create a virtual environment and install all necessary libraries.

2.  **Run the App**:
    Double-click `run_gui.bat`. This will launch the graphical interface in your browser.

## 🛠 Configuration

-   **Service Account**: Ensure `src/gcp-service-account/service_account.json` exists.
-   **Sheet IDs**: Modify `config.json` to change source/target Sheet IDs or the default Year.

## 🧩 logic Notes

-   **Date Extraction**: The tool uses the **Tab Name** (e.g., `2212` for Dec 22nd) as the primary date source.
    -   If a tab is named "2212", *all* rows in that tab are assigned to Dec 22nd.
    -   This overrides any conflicting dates found in column headers (e.g., "12.12").
-   **Columns**: Column names are normalized (lowercase, snake_case). "Total Account Followers" is special-cased.

## 🐛 Troubleshooting

-   **Connecting hangs**: If the app hangs at "Connecting...", check your internet connection and ensure the service account file is valid.
-   **Streamlit not recognized**: Run `setup_env.bat` again to repair the environment.
