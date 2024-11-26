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
        
        # Gmail API scope
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        self.service = None
        
        self.setup_gui()
        self.authenticate()
        
    def setup_gui(self):
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
        
        # Send email button
        send_btn = ttk.Button(self.root, text="Send Email", command=self.compose_email)
        send_btn.pack(pady=5)
        
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
                    'cred1.json', self.SCOPES)  # Ensure you have the updated SCOPES here
                creds = flow.run_local_server(port=0)
                # Send welcome email after new authentication
                self.service = build('gmail', 'v1', credentials=creds)
                profile = self.service.users().getProfile(userId='me').execute()
                user_email = profile['emailAddress']
                self.send_welcome_email(user_email)
                
            # Save credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    
        # Create Gmail API service
        self.service = build('gmail', 'v1', credentials=creds)
        
        # Fetch emails after authentication
        self.fetch_emails()

    def send_welcome_email(self, user_email):
        """
        Send an automated welcome email to new users.
        """
        try:
            # Create message container
            message = MIMEMultipart()
            message['to'] = user_email
            message['from'] = user_email  # Add from field
            message['subject'] = 'Welcome to Our Platform!'

            # Create the HTML version of your message
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

            # Convert the message to MIMEText
            mime_text = MIMEText(html_content, 'html')
            message.attach(mime_text)

            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Create the message body
            create_message = {
                'raw': raw_message
            }

            # Send the email
            send_message = (self.service.users().messages()
                          .send(userId="me", body=create_message).execute())
            
            print(f"Welcome email sent successfully to {user_email}")
            messagebox.showinfo("Success", f"Welcome email sent to {user_email}")
            return send_message

        except Exception as e:
            print(f"An error occurred while sending welcome email: {e}")
            messagebox.showerror("Error", f"Failed to send welcome email: {str(e)}")
            return None
        
    def fetch_emails(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            # Request emails from Gmail API
            results = self.service.users().messages().list(
                userId='me', maxResults=10, labelIds=['INBOX']
            ).execute()
            
            # Check the response
            print("Results:", results)  # Debugging line
            
            messages = results.get('messages', [])
            
            if not messages:
                messagebox.showinfo("No Emails", "No emails found in the inbox.")
            
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                ).execute()
                
                # Check the full message response
                print("Message:", msg)  # Debugging line
                
                # Extract email details from headers
                headers = msg['payload']['headers']
                
                # Safe extraction of subject, sender, and date
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'No Date')
                
                # Parse date to more readable format
                parsed_date = email.utils.parsedate_to_datetime(date)
                formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                
                # Insert into treeview
                self.tree.insert('', tk.END, values=(sender, subject, formatted_date), iid=message['id'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch emails: {str(e)}")
            print(f"Error: {str(e)}")  # Print the full exception to the console
                
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
                            ).decode('utf-8', errors='replace')
                            break
            else:
                if 'data' in message['payload']['body']:
                    body = base64.urlsafe_b64decode(
                        message['payload']['body']['data']
                    ).decode('utf-8', errors='replace')
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
        # Create a new window to compose an email
        compose_window = tk.Toplevel(self.root)
        compose_window.title("Compose Email")
        compose_window.geometry("400x300")
        
        # Add recipient, subject, and body fields
        tk.Label(compose_window, text="To:").pack(pady=5)
        to_entry = tk.Entry(compose_window, width=50)
        to_entry.pack(pady=5)
        
        tk.Label(compose_window, text="Subject:").pack(pady=5)
        subject_entry = tk.Entry(compose_window, width=50)
        subject_entry.pack(pady=5)
        
        tk.Label(compose_window, text="Body:").pack(pady=5)
        body_text = tk.Text(compose_window, width=50, height=10)
        body_text.pack(pady=5)
        
        # Send button
        send_button = ttk.Button(compose_window, text="Send", command=lambda: self.send_email(to_entry.get(), subject_entry.get(), body_text.get("1.0", tk.END), compose_window))
        send_button.pack(pady=10)
        
    def send_email(self, to, subject, body, compose_window):
        try:
            # Create MIME message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            msg = MIMEText(body)
            message.attach(msg)
            
            # Encode the message to base64
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send the email using Gmail API
            send_message = self.service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            print(f"Message Id: {send_message['id']}")
            
            # Close the compose window
            compose_window.destroy()
            messagebox.showinfo("Success", "Email sent successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GmailApp(root)
    root.mainloop()
