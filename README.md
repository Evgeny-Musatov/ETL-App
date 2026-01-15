# Meta Table ETL Cleaning

This tool automates the process of reading data from Source Google Sheets, cleaning/transforming it, and writing it to a Target Google Sheet.


## 🚀 Quick Start

### Windows
1.  **Setup**: Double-click `setup_env.bat` (First time only).
2.  **Run**: Double-click `run_app.bat`.

### macOS
1.  **Setup**: Double-click `setup_env.sh` (First time only).
    > **Note**: If it doesn't run, open Terminal, navigate to the folder, and run:
    > ```bash
    > chmod +x setup_env.sh
    > ./setup_env.sh
    > ```
2.  **Run**: Double-click `run_app.command`.
    > **Note**: If it doesn't run, open Terminal, navigate to the folder, and run:
    > ```bash
    > chmod +x run_app.command
    > ```

## 🛠 Configuration

-   **Service Account**: Ensure `src/gcp-service-account/service_account.json` exists.
-   **Sheet IDs**: Modify `config.json`. If missing, the app will generate a skeleton `config.json` on first run.

## 🧩 Logic Notes

-   **Date Extraction**: The tool uses the **Tab Name** (e.g., `2212` for Dec 22nd) as the primary date source.
    -   If a tab is named "2212", *all* rows in that tab are assigned to Dec 22nd.
    -   This overrides any conflicting dates found in column headers (e.g., "12.12").
-   **Columns**: Column names are normalized (lowercase, snake_case). "Total Account Followers" is special-cased.

## 🐛 Troubleshooting

-   **App Won't Start (Windows)**: If the app opens and closes immediately or says "Address already in use":
    1.  Double-click `kill_app.bat` to force-close any stuck background processes.
    2.  Try `run_app.bat` again.
-   **Connecting hangs**: If the app hangs at "Connecting...", check your internet connection and ensure the service account file is valid.

