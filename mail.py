import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, recipient_emails, subject, message):
    """
    Sends an email using SMTP.

    Parameters:
        sender_email (str): Email address of the sender.
        recipient_emails (list): List of email addresses of the recipients.
        subject (str): Subject of the email.
        message (str): Content of the email message.

    Returns:
        bool: True if the email is sent successfully, False otherwise.
    """

    # Email server settings (example for Gmail)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    username = 'subrat.plaksha@gmail.com'
    password = 'ewsmlxssjhslnzng'

    # Create a MIMEText object to represent the email content
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipient_emails)
    msg['Subject'] = subject

    # Attach the message to the email
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Connect to the email server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Encrypt the connection
        server.login(username, password)
        server.sendmail(sender_email, recipient_emails, msg.as_string())
        server.quit()

        print("Email sent successfully.")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# Example usage:
if __name__ == "__main__":
    sender_email = 'subratsaxenaofficial@gmail.com'
    recipient_emails = ['subratsaxena9@gmail.com'] # , 'recipient2@example.com'
    subject = 'Test Email'
    message = 'This is a test email sent from Python.'

    send_email(sender_email, recipient_emails, subject, message)
