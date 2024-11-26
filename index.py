import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import email


class GmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Inbox Viewer")
        self.root.geometry("800x600")
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        self.service = None
        self.setup_gui()
        self.authenticate()

    def setup_gui(self):
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(self.main_frame, columns=('From', 'Subject', 'Date'), show='headings')
        self.tree.heading('From', text='From')
        self.tree.heading('Subject', text='Subject')
        self.tree.heading('Date', text='Date')
        self.tree.column('From', width=200)
        self.tree.column('Subject', width=400)
        self.tree.column('Date', width=150)
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        refresh_btn = ttk.Button(self.root, text="Refresh", command=self.fetch_emails)
        refresh_btn.pack(pady=5)
        send_btn = ttk.Button(self.root, text="Send Email", command=self.compose_email)
        send_btn.pack(pady=5)
        self.tree.bind('<Double-1>', self.show_email_content)

    def authenticate(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('cred1.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                self.service = build('gmail', 'v1', credentials=creds)
                profile = self.service.users().getProfile(userId='me').execute()
                user_email = profile['emailAddress']
                self.send_welcome_email(user_email)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        self.service = build('gmail', 'v1', credentials=creds)
        self.fetch_emails()

    def send_welcome_email(self, user_email):
        try:
            message = MIMEMultipart()
            message['to'] = user_email
            message['from'] = user_email
            message['subject'] = 'Welcome to Our Platform!'
            html_content = """
            <html>
              <body>
                <h2>Welcome to Our Platform!</h2>
                <p>Dear User,</p>
                <p>Thank you for signing up! We're excited to have you on board.</p>
                <p>Here are a few things you can do to get started:</p>
                <ul>
                  <li>Complete your profile</li>
                  <li>Explore our features</li>
                  <li>Connect with other users</li>
                </ul>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Best regards,<br>Vaishvi (231081074) , Zoher (231080077)</p>
              </body>
            </html>
            """
            mime_text = MIMEText(html_content, 'html')
            message.attach(mime_text)
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            create_message = {'raw': raw_message}
            self.service.users().messages().send(userId="me", body=create_message).execute()
            messagebox.showinfo("Success", f"Welcome email sent to {user_email}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send welcome email: {str(e)}")

    def fetch_emails(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            results = self.service.users().messages().list(userId='me', maxResults=10, labelIds=['INBOX']).execute()
            messages = results.get('messages', [])
            if not messages:
                messagebox.showinfo("No Emails", "No emails found in the inbox.")
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'No Date')
                parsed_date = email.utils.parsedate_to_datetime(date)
                formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                self.tree.insert('', tk.END, values=(sender, subject, formatted_date), iid=message['id'])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch emails: {str(e)}")

    def show_email_content(self, event):
        item_id = self.tree.selection()[0]
        try:
            message = self.service.users().messages().get(userId='me', id=item_id, format='full').execute()
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
                            break
            else:
                if 'data' in message['payload']['body']:
                    body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='replace')
                else:
                    body = "No text content available"
            content_window = tk.Toplevel(self.root)
            content_window.title("Email Content")
            content_window.geometry("600x400")
            text_widget = tk.Text(content_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, body)
            text_widget.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch email content: {str(e)}")

    def compose_email(self):
        compose_window = tk.Toplevel(self.root)
        compose_window.title("Compose Email")
        compose_window.geometry("400x600")
        tk.Label(compose_window, text="To:").pack(pady=5)
        to_entry = tk.Entry(compose_window, width=50)
        to_entry.pack(pady=5)
        tk.Label(compose_window, text="Subject:").pack(pady=5)
        subject_entry = tk.Entry(compose_window, width=50)
        subject_entry.pack(pady=5)
        tk.Label(compose_window, text="Body:").pack(pady=5)
        body_text = tk.Text(compose_window, width=50, height=10)
        body_text.pack(pady=5)
        send_button = ttk.Button(compose_window, text="Send", command=lambda: self.send_email(to_entry.get(), subject_entry.get(), body_text.get("1.0", tk.END), compose_window))
        send_button.pack(pady=10)

    def send_email(self, to, subject, body, compose_window):
        try:
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            msg = MIMEText(body)
            message.attach(msg)
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            compose_window.destroy()
            messagebox.showinfo("Success", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = GmailApp(root)
    root.mainloop()
