import streamlit as st
import pandas as pd
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
st.title("Email Automation")

# File uploader for the CSV file
csv_file = st.file_uploader("Upload CSV file with emails", type=["csv"])

# File uploader for the PDF (ensuring the PDF will be renamed "instructions.pdf")
pdf_file = st.file_uploader("Upload PDF to attach", type=["pdf"])

# Additional information input
additional_info = st.text_area("Test Link:")

if st.button("Send Emails"):
    if csv_file and pdf_file and additional_info:
        # Load the CSV file
        df = pd.read_csv(csv_file)

        # Ensure the CSV has the required columns
        required_columns = {'Name', 'Email', 'Date of Interview', 'Time of Interview'}
        if required_columns.issubset(df.columns):
            candidates = df[['Name', 'Email', 'Date of Interview', 'Time of Interview']].dropna()

            # Save the uploaded PDF to a local directory as "instructions.pdf"
            pdf_path = os.path.join(os.getcwd(), "instructions.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            success_count = 0
            fail_count = 0

            # Send email to each candidate
            for _, row in candidates.iterrows():
                try:
                    send_email(
                        row['Email'].strip(),
                        row['Name'].strip(),
                        row['Date of Interview'].strip(),
                        row['Time of Interview'].strip(),
                        pdf_path,
                        additional_info
                    )
                    success_count += 1
                except Exception as e:
                    st.error(f"Failed to send email to {row['Email'].strip()}: {str(e)}")
                    fail_count += 1

            st.success(f"Emails sent successfully to {success_count} addresses.")
            if fail_count > 0:
                st.warning(f"Failed to send to {fail_count} addresses.")
        else:
            st.error(f"The CSV file must contain the following columns: {', '.join(required_columns)}.")
    else:
        st.warning("Please upload the CSV file, the PDF, and enter additional information.")
