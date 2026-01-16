# Meta Table ETL Cleaning

This tool automates the process of reading data from Source Google Sheets, cleaning/transforming it, and writing it to a Target Google Sheet.

The application provides a **Streamlit web interface** with two main pages:
- **Run Pipeline**: Execute the ETL process with date range selection
- **Manage Target Sheet**: Delete old run tabs from the target sheet

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
    - Ensure the service account has access to both Source and Target sheets

2.  **Sheet IDs**: Edit `config.json` (created by setup script) and add your:
    - `source_sheet_id`: The Google Sheet ID to read data from
    - `target_sheet_id`: The Google Sheet ID to write cleaned data to

3.  **Optional Date Range**: You can set default date ranges in `config.json`:
    - `start_date`: Default start date in `YYYY-MM-DD` format (e.g., `"2024-01-01"`)
    - `end_date`: Default end date in `YYYY-MM-DD` format (e.g., `"2024-12-31"`)
    - If not provided, the app will automatically detect the latest tab date and look back 7 days

## 🧩 Logic Notes

### Date Extraction

The tool uses a **priority-based date extraction** system:

1.  **Tab Name** (highest priority): If a tab is named with a date format (e.g., `2212` for Dec 22nd, `12/12/2024`, `12-12-2024`), *all* rows in that tab are assigned to that date.
    - This overrides any conflicting dates found in column headers
    - Supported formats: `DDMM` (e.g., `2212`), `DD/MM/YYYY`, `DD-MM-YYYY`

2.  **Column Headers** (fallback): If the tab name doesn't contain a date, dates are parsed from column headers.
    - Supports formats: `12/12`, `12-12`, `December 12`, `Dec 12`, etc.

### Tab Naming Conventions

-   **Source Sheets**: Use date-based tab names (e.g., `2212`, `12/12/2024`) to identify which tabs to process for a date range
-   **Target Sheets**: Use run-based tab names (e.g., `Run 1 - [DD/MM/YYYY HH:MM:SS]`)
    - The app automatically increments run numbers (finds highest "Run N" and creates "Run N+1")
    - Old format also supported: `run N [YYYY-MM-DD_HH-MM-SS]`

### Column Normalization

-   All column names are converted to **lowercase snake_case** (e.g., "Total Account Followers" → `total_account_followers`)
-   Special handling: Headers containing "Total Account Followers" are normalized to `total_account_followers`
-   Duplicate column names get numeric suffixes (`column_1`, `column_2`, etc.)
-   Columns with >30% numeric content are automatically converted to numeric types

## 🐛 Troubleshooting

### App Won't Start

-   **Windows**: If the app opens and closes immediately or says "Address already in use":
    1.  Close any other Streamlit instances that might be running.
    2.  Try `run_app.bat` again.

-   **macOS**: If you get a Gatekeeper warning when double-clicking:
    1.  Remove quarantine attributes from both scripts:
        ```bash
        xattr -d com.apple.quarantine setup_env.command
        xattr -d com.apple.quarantine run_app.command
        ```
    2.  Or right-click and select "Open" to bypass Gatekeeper once (works for each file individually).
    3.  If you get "Permission denied", run: `chmod +x run_app.command`

### Virtual Environment Not Found

-   **Symptom**: Script exits with "Virtual environment (.venv) not found"
-   **Solution**: Run the setup script first (`setup_env.command` on macOS or `setup_env.bat` on Windows)

### Connection Issues

-   **Connecting hangs**: If the app hangs at "Connecting...":
    - Check your internet connection
    - Verify the service account file exists and is valid at `src/gcp-service-account/service_account.json`
    - Ensure the service account has access to both Source and Target sheets

### Data Issues

-   **No Data Found**: If you see "No data found for the selected range":
    - Check that the date range includes valid tab dates
    - Verify tab names match expected formats (DDMM, DD/MM/YYYY, DD-MM-YYYY)
    - Ensure the source sheet has data in the selected tabs

### Configuration Issues

-   **Config file missing**: If you see an error about `config.json` not found:
    - Run the setup script first (`setup_env.command` on macOS or `setup_env.bat` on Windows)
    - The setup script will create `config.json` with a skeleton structure
    - Edit `config.json` and add your Google Sheet IDs

