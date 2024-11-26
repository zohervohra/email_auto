# Gmail Inbox Viewer and Email Sender

## Overview
The **Gmail Inbox Viewer and Email Sender** is a Python-based GUI application developed using `tkinter` and the Gmail API. It allows users to authenticate via their Gmail account, view recent emails, send new emails, and read email content. The application is a practical demonstration of integrating Google's Gmail API with Python to build a functional desktop client.

## Features
1. **View Inbox**: Displays the most recent emails with details such as sender, subject, and date.
2. **Send Emails**: Provides a user-friendly interface to compose and send emails directly through the app.
3. **Read Emails**: Double-click on an email to view its content in a new window.
4. **Automated Welcome Email**: Sends a welcome email upon first-time authentication.
5. **Refresh Button**: Update the inbox view with the latest emails.

## Prerequisites

1. **Python**  
   Ensure you have Python 3.7 or later installed on your system.  
   You can download Python from [Python.org](https://www.python.org/downloads/).  

2. **Required Libraries**  
   Install the necessary Python libraries by running:  
   ```bash
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

3. **Enable Gmail API**  
   You must set up Gmail API access to use this project. Instructions are provided below.

---

## Setup Guide

### Step 1: Clone the Repository

Clone this repository to your local machine:  
```bash
git clone https://github.com/your-username/your-repository.git
```

Navigate to the project folder:  
```bash
cd your-repository
```

---

### Step 2: Get Your `cred1.json`

To use the Gmail API, you need a credentials file (`cred1.json`). Follow these steps to create and download it:  

1. **Enable the Gmail API**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Navigate to **API & Services > Library**.
   - Search for "Gmail API" and enable it.

2. **Set Up OAuth Credentials**:
   - Go to **API & Services > Credentials** in the Google Cloud Console.
   - Click **Create Credentials** > **OAuth Client ID**.
   - Configure the consent screen with basic details (e.g., app name, email).
   - Choose "Desktop App" as the application type and create the credentials.

3. **Download the Credentials**:
   - After creating the OAuth client, download the JSON file.
   - Rename it to `cred1.json` and place it in the project directory.

---

### Step 3: Run the Application

1. Authenticate with Gmail:  
   The first time you run the script, you will be redirected to a Google login page to grant access to your Gmail account.  

2. Run your script:  
   ```bash
   python your_script.py
   ```

3. The program will store an access token locally for subsequent use.

---

## Learning Outcomes
By working on this project, we:
- Gained hands-on experience with the Gmail API, including OAuth2 authentication.
- Learned to integrate RESTful APIs into Python projects for real-world applications.
- Explored GUI design using `tkinter` to create interactive and user-friendly interfaces.
- Understood MIME format and email message construction for sending rich content.
- Improved debugging skills by handling API errors and GUI exceptions gracefully.
- Enhanced project documentation skills, highlighting reusability and practical use cases.

## Reusability and Practical Use Cases
This project is designed to be reusable and extendable for other applications:
- **Custom Email Clients**: Build a tailored email client with additional features like sorting, filtering, or email categorization.
- **Bulk Email Automation**: Extend the app to support sending bulk emails for marketing campaigns or announcements.
- **Learning Tool**: Use it as a beginner-friendly project for learning `tkinter`, Google APIs, and email protocols.
- **Enterprise Applications**: Integrate similar functionality into larger systems, such as CRM platforms or customer support tools.
- **Notification Systems**: Adapt the email-sending functionality for automated notifications in projects.