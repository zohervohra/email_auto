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
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        
        # Send Email button
        send_email_btn = ttk.Button(self.root, text="Send Email", command=self.open_email_composer)
        send_email_btn.pack(pady=5)
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.show_email_content)


    def open_email_composer(self):
        """
        Open a new window to compose and send an email.
        """
        def handle_send():
            # Get inputs
            recipient = to_entry.get().strip()
            subject = subject_entry.get().strip()
            body = body_text.get("1.0", tk.END).strip()
            
            if not recipient or not subject or not body:
                # Show error if any field is empty
                messagebox.showerror("Error", "All fields (To, Subject, Message) must be filled.")
                return
            
            # Call the send_email method
            success = self.send_email(recipient, subject, body)
            if success:
                # Close the composer window on success
                composer_window.destroy()

        composer_window = tk.Toplevel(self.root)
        composer_window.title("Compose Email")
        composer_window.geometry("500x400")
        
        # Fields for recipient, subject, and body
        ttk.Label(composer_window, text="To:").pack(anchor=tk.W, padx=10, pady=5)
        to_entry = ttk.Entry(composer_window, width=50)
        to_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(composer_window, text="Subject:").pack(anchor=tk.W, padx=10, pady=5)
        subject_entry = ttk.Entry(composer_window, width=50)
        subject_entry.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(composer_window, text="Message:").pack(anchor=tk.W, padx=10, pady=5)
        body_text = tk.Text(composer_window, height=15)
        body_text.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        # Send button
        send_btn = ttk.Button(
            composer_window, 
            text="Sendi", 
            command=handle_send
        )
        send_btn.pack(pady=10)

        labeli = ttk.Label(composer_window, text="Note: Please enter the email address in the 'To' field")
        labeli.pack(pady=5)

    def send_email(self, recipient, subject, body):
        """
        Send an email using the Gmail API.
        """
        try:
            # Create email structure
            from email.mime.text import MIMEText
            import base64

            message = MIMEText(body)
            message['to'] = recipient
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            create_message = {'raw': raw_message}

            # Use Gmail API to send the email
            self.service.users().messages().send(userId="me", body=create_message).execute()

            messagebox.showinfo("Success", "Email sent successfully!")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")
            return False



    def send_email(self, recipient, subject, message_body):
        """
        Send an email using the Gmail API.
        """
        try:
            # Create the email content
            message = MIMEMultipart()
            message['to'] = recipient
            message['from'] = "me"
            message['subject'] = subject
            
            # Add the message body
            message.attach(MIMEText(message_body, 'plain'))
            
            # Encode the email
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            create_message = {'raw': raw_message}
            
            # Send the email
            send_message = self.service.users().messages().send(userId="me", body=create_message).execute()
            print(f"Email sent successfully to {recipient}")
            messagebox.showinfo("Success", f"Email sent successfully to {recipient}")
        
        except Exception as e:
            print(f"An error occurred while sending email: {e}")
            messagebox.showerror("Error", f"Failed to send email: {e}")

    
    
    def authenticate(self):
        creds = None
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            token_path = os.path.join(current_dir, 'token.pickle')
            credentials_path = os.path.join(current_dir, 'credentials.json')

            # Debug prints
            print(f"Looking for credentials at: {credentials_path}")
            print(f"Looking for token at: {token_path}")
            
            # Check for token.pickle
            if os.path.exists(token_path):
                try:
                    with open(token_path, 'rb') as token:
                        creds = pickle.load(token)
                    print("Loaded existing token.pickle")
                except Exception as e:
                    print(f"Error loading token.pickle: {e}")
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    creds = None

            # If credentials are not valid or don't exist
            if not creds or not creds.valid:
                # Check for credentials.json first
                if not os.path.exists(credentials_path):
                    messagebox.showerror(
                        "Error", 
                        f"credentials.json not found at {credentials_path}!\n\n"
                        "Please ensure the file exists and has proper permissions."
                    )
                    self.root.quit()
                    return

                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        print("Refreshed expired credentials")
                    except Exception as e:
                        print(f"Error refreshing credentials: {e}")
                        creds = None
                
                if not creds:
                    try:
                        print("Attempting to create new credentials flow...")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        print("Successfully created new credentials")

                        # Get user email from credentials
                        try:
                            self.service = build('gmail', 'v1', credentials=creds)
                            profile = self.service.users().getProfile(userId='me').execute()
                            user_email = profile['emailAddress']
                            print(f"User email: {user_email}")
                            
                            # Send welcome email after new authentication
                            self.send_welcome_email(user_email)
                            
                        except Exception as e:
                            print(f"Error getting user profile: {e}")

                    except Exception as e:
                        error_msg = (
                            f"Failed to authenticate: {str(e)}\n\n"
                            f"Credentials path: {credentials_path}\n"
                            "Please ensure:\n"
                            "1. credentials.json exists in the same directory as this script\n"
                            "2. The file has proper read permissions\n"
                            "3. The file is valid and not corrupted"
                        )
                        messagebox.showerror("Authentication Error", error_msg)
                        self.root.quit()
                        return

                # Save valid credentials
                try:
                    with open(token_path, 'wb') as token:
                        pickle.dump(creds, token)
                    print("Saved new token.pickle")
                except Exception as e:
                    print(f"Error saving token.pickle: {e}")

            # Create Gmail API service
            print("Creating Gmail API service...")
            self.service = build('gmail', 'v1', credentials=creds)
            
            # Test the connection
            try:
                self.service.users().getProfile(userId='me').execute()
                print("Authentication successful!")
            except Exception as e:
                messagebox.showerror(
                    "Connection Error",
                    f"Failed to connect to Gmail API: {str(e)}"
                )
                self.root.quit()
                return

            # Fetch emails after successful authentication
            self.fetch_emails()

        except Exception as e:
            error_msg = (
                f"An unexpected error occurred: {str(e)}\n\n"
                "Please check:\n"
                "1. Internet connection\n"
                "2. File permissions\n"
                "3. Validity of credentials.json"
            )
            messagebox.showerror("Authentication Error", error_msg)
            self.root.quit()

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
        try:
        # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            print("Fetching emails...")
            results = self.service.users().messages().list(
            userId='me', maxResults=10, labelIds=['INBOX']
            ).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No emails found")
                messagebox.showinfo("Info", "No emails found in the inbox.")
                return

            for message in messages:
                try:
                    msg = self.service.users().messages().get(
                    userId='me', id=message['id'], format='full'
                    ).execute()
                    headers = msg['payload']['headers']
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

                # Parse and format date
                    try:
                        parsed_date = email.utils.parsedate_to_datetime(date)
                        formatted_date = parsed_date.strftime('%Y-%m-%d %H:%M')
                    except:
                        formatted_date = "Invalid Date"

                    self.tree.insert('', tk.END, values=(sender, subject, formatted_date), iid=message['id'])
                except Exception as e:
                    print(f"Error processing message: {e}")

                print("Emails fetched successfully")
        except Exception as e:
                print(f"Error fetching emails: {e}")
                messagebox.showerror("Error", f"Could not fetch emails: {e}")

            
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
            
    def process_new_user_signup(self, user_email):
        """
        Handle new user signup process including sending welcome email.
        Call this method when a new user signs up.
        """
        try:
            # Send welcome email
            self.send_welcome_email(user_email)
            
            # You can add additional new user processing here
            messagebox.showinfo("Success", f"Welcome email sent to {user_email}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process new user: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GmailApp(root)
    root.mainloop()