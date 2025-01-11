

# LinkedIn Job Application Bot

An automated bot that applies for jobs on LinkedIn based on user-defined criteria. This project uses Selenium for browser automation and OpenAI for intelligent handling of job application questions.

---

## Features

- **Automated Job Search**: Generates job URLs based on keywords, location, experience levels, and more.
- **Easy Application**: Automatically fills in application forms and submits applications.
- **Question Handling**: Uses OpenAI to intelligently respond to additional application questions.
- **Retry Logic**: Robust mechanisms to handle common Selenium issues like stale elements.
- **Error Logging**: Captures screenshots of errors for debugging.
- **Customizable**: User-defined configurations in `config.py`.

---

## Project Structure

```plaintext
/project-root
├── config.py               # Configuration file for user preferences
├── utils.py                # Utility functions and helper modules
├── linkedin.py             # Main script to run the bot
├── /data                   # Contains URL and logs
├── /error_screenshots      # Stores screenshots of errors
├── README.md               # Documentation
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (optional)
```

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+**
2. **Firefox Browser** and **Geckodriver**
   - [Download Geckodriver](https://github.com/mozilla/geckodriver/releases)
3. **LinkedIn Account** with saved login cookies.
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### Configuration

Edit the `config.py` file to set up your preferences:

- **Job Search Criteria**:
  - Keywords, location, experience level, job type, etc.
- **Browser Settings**:
  - Enable or disable headless mode.
- **LinkedIn Credentials**:
  - Use pre-saved cookies for authentication.

Example:
```python
headless = False
firefox_profile_path = "/path/to/your/firefox/profile"
location = ["New York"]
keywords = ["Data Scientist", "Machine Learning"]
experienceLevels = ["Entry level"]
jobType = ["Full-time"]
remote = ["On-site"]
```

---

### Running the Bot

1. Save your LinkedIn cookies to a file named `linkedin_cookies.json`.
2. Run the main script:
   ```bash
   python linkedin.py
   ```

---

## How It Works

1. **Setup**:
   - The bot logs in using your saved cookies and sets up the search criteria.
2. **Job Search**:
   - Generates job URLs based on your preferences.
3. **Application**:
   - Visits each job link, extracts job details, and attempts to apply.
   - Handles dropdowns and text questions intelligently using OpenAI.
4. **Logs and Errors**:
   - Successful applications are logged in `/data`.
   - Screenshots of errors are saved in `/error_screenshots`.

---

## Environment Variables

Create a `.env` file to store sensitive information:
```plaintext
OPENAI_API_KEY=your_openai_api_key
```

---

## Troubleshooting

- **Missing Imports**:
  Ensure all dependencies are installed using:
  ```bash
  pip install -r requirements.txt
  ```

- **Driver Issues**:
  - Ensure `geckodriver` is installed and added to your system path.
  - Verify your Firefox version is compatible with the installed `geckodriver`.

- **LinkedIn Authentication**:
  - Verify your cookies are correctly saved in `linkedin_cookies.json`.
  - Use a valid Firefox profile path in `config.py`.


## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Acknowledgments

- **Selenium** for browser automation.
- **OpenAI** for intelligent question handling.

--- 

Let me know if you'd like to adjust or expand this further!