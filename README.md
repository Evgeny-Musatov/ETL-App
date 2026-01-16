# Meta Table ETL Cleaning

This tool automates the process of reading data from Source Google Sheets, cleaning/transforming it, and writing it to a Target Google Sheet.


## 🚀 Quick Start

### Windows
1.  **Setup**: Double-click `setup_env.bat` (First time only).
2.  **Run**: Double-click `run_app.bat`.

### macOS
1.  **Setup**: Double-click `setup_env.command` (First time only).
    > **Note**: If you get a Gatekeeper warning, remove quarantine attributes first:
    > ```bash
    > xattr -d com.apple.quarantine setup_env.command
    > xattr -d com.apple.quarantine run_app.command
    > ```
    > Or if it doesn't run, open Terminal, navigate to the folder, and run:
    > ```bash
    > chmod +x setup_env.command
    > ./setup_env.command
    > ```
2.  **Run**: Double-click `run_app.command`.
    > **Note**: If it doesn't run, open Terminal, navigate to the folder, and run:
    > ```bash
    > chmod +x run_app.command
    > ```

## 🛠 Configuration

After running the setup script, you need to configure:

1.  **Service Account**: Place your Google Cloud service account JSON file at:
    `src/gcp-service-account/service_account.json`
2.  **Sheet IDs**: Edit `config.json` (created by setup script) and add your:
    - `source_sheet_id`: The Google Sheet ID to read data from
    - `target_sheet_id`: The Google Sheet ID to write cleaned data to

## 🧩 Logic Notes

-   **Date Extraction**: The tool uses the **Tab Name** (e.g., `2212` for Dec 22nd) as the primary date source.
    -   If a tab is named "2212", *all* rows in that tab are assigned to Dec 22nd.
    -   This overrides any conflicting dates found in column headers (e.g., "12.12").
-   **Columns**: Column names are normalized (lowercase, snake_case). "Total Account Followers" is special-cased.

## 🐛 Troubleshooting

-   **App Won't Start (Windows)**: If the app opens and closes immediately or says "Address already in use":
    1.  Close any other Streamlit instances that might be running.
    2.  Try `run_app.bat` again.
-   **App Won't Start (macOS)**: If you get a Gatekeeper warning when double-clicking:
    1.  Remove quarantine attributes from both scripts:
        ```bash
        xattr -d com.apple.quarantine setup_env.command
        xattr -d com.apple.quarantine run_app.command
        ```
    2.  Or right-click and select "Open" to bypass Gatekeeper once (works for each file individually).
-   **Connecting hangs**: If the app hangs at "Connecting...", check your internet connection and ensure the service account file is valid.
-   **Config file missing**: If you see an error about `config.json` not found, run the setup script first (`setup_env.command` on macOS or `setup_env.bat` on Windows).

