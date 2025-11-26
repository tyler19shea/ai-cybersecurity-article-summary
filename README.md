# AI Cybersecurity Article Summary Bot

This project is a Python-based bot that automates the process of gathering, analyzing, and summarizing cybersecurity articles from various sources. It uses an AI model to rank the articles by importance and sends a daily summary report via email.

## Features

- **Article Aggregation:** Fetches the latest articles from a configurable list of RSS feeds.
- **AI-Powered Analysis:** Leverages OpenAI's GPT model to perform in-depth analysis, summarization, and importance ranking of the gathered articles.
- **Customizable AI Persona:** The behavior of the AI analyst can be easily customized by modifying the `system_prompt` file.
- **Email Reporting:** Automatically sends a formatted HTML email containing the top cybersecurity articles of the day.
- **Duplicate Prevention:** Keeps track of processed articles to ensure that the same article is not analyzed multiple times.
- **Logging:** Maintains a log file (`CyberBot.log`) to record its operations and any potential errors.

## How It Works

1.  The main script, `cyber-article-bot.py`, is executed.
2.  It loads a list of RSS feed URLs and fetches the latest entries.
3.  For each new article (i.e., one not found in `processed_links.txt`), it downloads the full article text.
4.  The text from all new articles is combined into a single payload and sent to the OpenAI API. A "system prompt" guides the AI to act as a cybersecurity analyst, summarizing and ranking the articles.
5.  The AI's response, which is a ranked list of summarized articles, is saved to `message.md`.
6.  The `sendemail.py` module is invoked, which reads the content of `message.md`, converts it from Markdown to HTML, and sends it as an email.
7.  The links of the newly processed articles are appended to `processed_links.txt` to prevent reprocessing in the future.

## Setup and Usage

### Prerequisites

- Python 3.x

### 1. Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ai-cybersecurity-article-summary.git
    cd ai-cybersecurity-article-summary
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 2. Configuration

1.  **Create a `.env` file** in the root of the project directory. This file will store your secret credentials.

2.  **Add the following environment variables** to your `.env` file:

    ```
    OPENAI_API_KEY="your_openai_api_key"
    FROM_EMAIL="your_email@gmail.com"
    PASSWORD_EMAIL="your_gmail_app_password"
    TO_EMAIL="recipient_email@example.com"
    ```

    - `OPENAI_API_KEY`: Your API key from OpenAI.
    - `FROM_EMAIL`: The Gmail address the report will be sent from.
    - `PASSWORD_EMAIL`: You will need to generate a Gmail "App Password" for this. Standard passwords will not work with `smtplib` due to Google's security policies.
    - `TO_EMAIL`: The email address that will receive the daily report.

3.  **(Optional) Customize Article Sources:**
    Modify the `RSS_URLS` list in `cyber-article-bot.py` to add or remove RSS feeds.

4.  **(Optional) Customize AI Behavior:**
    Edit the `system_prompt` file to change the instructions given to the AI analyst.

### 3. Running the Bot

To run the bot manually, execute the main script:
```bash
python cyber-article-bot.py
```

### 4. Scheduling

For automatic daily execution, you can schedule the script using:
- **Cron** on Linux or macOS.
- **Task Scheduler** on Windows.

Example cron job to run the script every day at 8:00 AM:
```
0 8 * * * /usr/bin/python /path/to/your/project/cyber-article-bot.py
```

## Project Files

- **`cyber-article-bot.py`**: The main script that orchestrates the entire process.
- **`sendemail.py`**: A module that handles the sending of the final email report.
- **`requirements.txt`**: A list of the Python packages required for this project.
- **`system_prompt`**: A text file containing the instructions that define the AI's role and task.
- **`processed_links.txt`**: A file that stores the URLs of articles that have already been processed to prevent duplicates.
- **`message.md`**: A temporary file that holds the AI-generated analysis before it is emailed.
- **`CyberBot.log`**: The log file where all actions and errors are recorded.
- **`.gitignore`**: Specifies which files and directories to ignore for version control.
