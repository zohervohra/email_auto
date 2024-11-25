import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class GmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gmail Inbox Viewer")
        self.root.geometry("800x600")
        
        # Gmail API scope
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        self.service = None
        
        self.setup_gui()
        self.authenticate()
        
    def setup_gui(self):
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create email list
        self.tree = ttk.Treeview(self.main_frame, columns=('From', 'Subject', 'Date'), show='headings')
        self.tree.heading('From', text='From')
        self.tree.heading('Subject', text='Subject')
        self.tree.heading('Date', text='Date')
        
        # Configure column widths
        self.tree.column('From', width=200)
        self.tree.column('Subject', width=400)
        self.tree.column('Date', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_btn = ttk.Button(self.root, text="Refresh", command=self.fetch_emails)
        refresh_btn.pack(pady=5)
        
        # Compose email button
        compose_btn = ttk.Button(self.root, text="Compose Email", command=self.compose_email)
        compose_btn.pack(pady=5)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.show_email_content)
        
    def authenticate(self):
        creds = None
        # Load saved credentials if they exist
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If credentials are not valid or don't exist, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
                
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # Create Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)
        
        # Fetch emails after authentication
        self.fetch_emails()
            
    def fetch_emails(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Request emails from Gmail API
            results = self.service.users().messages().list(
                userId='me', maxResults=10, labelIds=['INBOX']
            ).execute()
            messages = results.get('messages', [])
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                ).execute()
                
                # Extract email details
                headers = msg['payload']['headers']
                subject = next(h['value'] for h in headers if h['name'] == 'Subject')
                sender = next(h['value'] for h in headers if h['name'] == 'From')
                date = next(h['value'] for h in headers if h['name'] == 'Date')
                
                # Parse date to more readable format
                parsed_date = email.utils.parsedate_to_datetime(date)
                formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                
                # Insert into treeview
                self.tree.insert('', tk.END, values=(sender, subject, formatted_date), 
                                iid=message['id'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch emails: {str(e)}")
            print(f"Error: {str(e)}")  # Print the error to console for debugging

    def show_email_content(self, event):
        item_id = self.tree.selection()[0]
        try:
            # Fetch full message content
            message = self.service.users().messages().get(
                userId='me', id=item_id, format='full'
            ).execute()
            
            # Extract message body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8')
                            break
            else:
                if 'data' in message['payload']['body']:
                    body = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8')
                else:
                    body = "No text content available"
            
            # Create new window to display email content
            content_window = tk.Toplevel(self.root)
            content_window.title("Email Content")
            content_window.geometry("600x400")
            
            # Add text widget
            text_widget = tk.Text(content_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Insert email content
            text_widget.insert(tk.END, body)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch email content: {str(e)}")
    
    def compose_email(self):
        compose_window = tk.Toplevel(self.root)
        compose_window.title("Compose Email")
        compose_window.geometry("500x400")
        
        # To field
        to_label = ttk.Label(compose_window, text="To:")
        to_label.pack(pady=5)
        to_entry = ttk.Entry(compose_window, width=40)
        to_entry.pack(pady=5)
        
        # Subject field
        subject_label = ttk.Label(compose_window, text="Subject:")
        subject_label.pack(pady=5)
        subject_entry = ttk.Entry(compose_window, width=40)
        subject_entry.pack(pady=5)
        
        # Body field
        body_label = ttk.Label(compose_window, text="Body:")
        body_label.pack(pady=5)
        body_text = tk.Text(compose_window, wrap=tk.WORD, height=10, width=40)
        body_text.pack(pady=5)
        
        # Send button
        send_btn = ttk.Button(compose_window, text="Send", command=lambda: self.send_email(to_entry, subject_entry, body_text))
        send_btn.pack(pady=10)
        
    def send_email(self, to_entry, subject_entry, body_text):
        to = to_entry.get()
        subject = subject_entry.get()
        body = body_text.get("1.0", tk.END)
        
        if not to or not subject or not body:
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            # Create MIME message
            msg = MIMEMultipart()
            msg['To'] = to
            msg['From'] = 'me'
            msg['Subject'] = subject
            
            # Attach body to the email
            msg.attach(MIMEText(body, 'plain'))
            
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Send email
            message = self.service.users().messages().send(
                userId='me', body={'raw': raw_message}
            ).execute()
            
            messagebox.showinfo("Success", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GmailApp(root)
    root.mainloop()
