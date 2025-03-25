import streamlit as st
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Email sending function
def send_email(to_email, candidate_name, interview_date, interview_time, pdf_path, additional_info):
    from_email = "ipams2.ohr@gmail.com"
    subject = "Welcome to IPAMS - Your Registration is Confirmed"
    
    # Email body with additional information, including candidate name, interview date, and time
    body = f"""
    Dear {candidate_name},

    Thank you for registering with IPAMS (Interview Performance Assessment using Gen AI)

    You have scheduled your interview on {interview_date} at {interview_time}.
    Please find the attached instructions PDF for more information on how to prepare for the interview process.
    Additionally, your test link is provided below.

    Test Link: {additional_info}  

    You will be able to access the test at your registered time, so please click the link during that time.
    If you have any questions or need assistance, feel free to reach out to us.

    Best regards,
    The IPAMS Team
    https://www.linkedin.com/company/ipams-2-o
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file with the name "instructions.pdf"
    with open(pdf_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="instructions.pdf")
        part['Content-Disposition'] = 'attachment; filename="instructions.pdf"'
        msg.attach(part)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, 'boyp arup ktud wtci')  # Replace with the actual password or use environment variables
        server.sendmail(from_email, to_email, msg.as_string())

# Streamlit application
st.title("Individual Email Automation")

# Input fields for candidate information
candidate_name = st.text_input("Candidate Name")
to_email = st.text_input("Candidate Email")
interview_date = st.date_input("Interview Date")
interview_time = st.time_input("Interview Time")

# File uploader for the PDF (ensuring the PDF will be renamed "instructions.pdf")
pdf_file = st.file_uploader("Upload PDF to attach", type=["pdf"])

# Additional information input
additional_info = st.text_area("Additional Information to include in the email (Test Link):")

if st.button("Send Email"):
    if candidate_name and to_email and interview_date and interview_time and pdf_file and additional_info:
        # Save the uploaded PDF to a local directory as "instructions.pdf"
        pdf_path = os.path.join(os.getcwd(), "instructions.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        try:
            # Send the email
            send_email(
                to_email.strip(),
                candidate_name.strip(),
                interview_date.strftime("%Y-%m-%d"),
                interview_time.strftime("%H:%M"),
                pdf_path,
                additional_info.strip()
            )
            st.success(f"Email sent successfully to {to_email}.")
        except Exception as e:
            st.error(f"Failed to send email to {to_email}: {str(e)}")
    else:
        st.warning("Please fill in all the fields and upload a PDF.")
