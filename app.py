import os
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import assemblyai as aai
from pypdf import PdfReader
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Set your API keys
google_api_key = 'AIzaSyD2_oxzOQQtcGDmW_Ul8E7mREi_LYYJO9I'
assemblyai_api_key = '458d04f86c934454bb8148b4f595a171'
os.environ['GOOGLE_API_KEY'] = google_api_key
aai.settings.api_key = assemblyai_api_key

# Configure the API client with your API key
genai.configure(api_key=google_api_key)

# ✅ Display Logo
def display_logos():
    st.image("iplogo.png", width=60) 
display_logos()

# ✅ Generate AI Questions from Resume
def generate_summary_prompt(comments):
    comments_text = " ".join(map(str, comments))
    prompt = f"""
    Ask the first question as: **Introduce yourself**
    Then, generate **5 Technical Questions** based on this resume (projects, skills)
    - Ask **2 SQL Questions**
    - Ask **2 DBMS Questions**
    - Total **10 questions**
    Provide only questions, no headings.
    {comments_text}
    """
    return prompt

def generate_text(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# ✅ Extract Text from Resume (PDF)
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = [page.extract_text() for page in reader.pages if page.extract_text()]
    return text

# ✅ Transcribe Video Answer
def transcribe_video(video_path):
    """Transcribes video using AssemblyAI"""
    transcriber = aai.Transcriber()
    try:
        transcript = transcriber.transcribe(video_path)
        return transcript.text
    except Exception as e:
        return f"Error in transcription: {str(e)}"

# ✅ Generate Interview Analysis Report (PDF)
def generate_pdf(analysis_report):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Interview Analysis Report", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, analysis_report)
    pdf_output_path = "Interview_Analysis_Report.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

# ✅ Send Email with PDF Attachment
def send_email(to_email, pdf_path):
    from_email = "your_email@gmail.com"
    subject = "Interview Analysis Report"
    body = "Please find the attached Interview Analysis Report."

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="Interview_Analysis_Report.pdf")
        part['Content-Disposition'] = 'attachment; filename="Interview_Analysis_Report.pdf"'
        msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, EMAIL_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())

# ✅ Streamlit App UI
st.title("🎯 IPAMS 2.O - AI Interview Guide")

# 🔹 **Candidate Info Form**
if 'name' not in st.session_state or 'email' not in st.session_state:
    st.header("Candidate Information")
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")

    if st.button("Submit Info"):
        if name and email:
            st.session_state.name = name
            st.session_state.email = email
            st.write(f"Hi {name}, please upload your resume.")
        else:
            st.error("Please enter both name and email.")

# 🔹 **Resume Upload**
else:
    st.write(f"Hi {st.session_state.name}, please upload your resume.")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    # ✅ Extract and Generate Questions
    if pdf_file and 'questions' not in st.session_state:
        with st.spinner("Extracting text from PDF..."):
            comments = extract_text_from_pdf(pdf_file)
            prompt = generate_summary_prompt(comments)

        st.write("Generating questions...")
        with st.spinner("Generating questions..."):
            questions = generate_text(prompt).split('\n')
            st.session_state.questions = [{"question": q, "answer": "", "transcribed": False} for q in questions if q.strip()]
            st.session_state.current_question_index = 0

    # ✅ Display Questions One by One
    if 'questions' in st.session_state:
        st.subheader("📝 Generated Questions")

        current_index = st.session_state.current_question_index
        question_data = st.session_state.questions[current_index]
        question = question_data["question"]
        st.write(f"{current_index + 1}. {question}")

        # 🎥 **Record & Upload Video Answer**
        components.html(f"""
            <div>
                <video id="video_{current_index}" width="320" height="240" controls></video>
                <br>
                <button id="record_{current_index}">Record</button>
                <button id="stop_{current_index}">Stop</button>
                <script>
                    let video = document.getElementById('video_{current_index}');
                    let recordButton = document.getElementById('record_{current_index}');
                    let stopButton = document.getElementById('stop_{current_index}');
                    let mediaRecorder;
                    let recordedChunks = [];

                    recordButton.onclick = async () => {{
                        let stream = await navigator.mediaDevices.getUserMedia({{ video: true, audio: true }});
                        video.srcObject = stream;
                        mediaRecorder = new MediaRecorder(stream);
                        mediaRecorder.start();
                        recordedChunks = [];

                        mediaRecorder.ondataavailable = (event) => {{
                            if (event.data.size > 0) {{
                                recordedChunks.push(event.data);
                            }}
                        }};

                        mediaRecorder.onstop = () => {{
                            let blob = new Blob(recordedChunks, {{ type: 'video/mp4' }});
                            let url = URL.createObjectURL(blob);
                            let a = document.createElement('a');
                            a.href = url;
                            a.download = 'video_{current_index}.mp4';
                            document.body.appendChild(a);
                            a.click();
                        }};
                    }};

                    stopButton.onclick = () => {{
                        mediaRecorder.stop();
                        video.srcObject.getTracks().forEach(track => track.stop());
                    }};
                </script>
            </div>
        """, height=400)

        # 🔹 **Upload Video for Transcription**
        video_file = st.file_uploader(f"Upload video answer for Question {current_index + 1}", type=["mp4"], key=f"uploader_{current_index}")

        if video_file and not question_data["transcribed"]:
            with st.spinner("Transcribing video..."):
                video_path = f"uploaded_video_{current_index + 1}.mp4"
                with open(video_path, "wb") as f:
                    f.write(video_file.read())
                transcript = transcribe_video(video_path)
                st.session_state.questions[current_index]["answer"] = transcript
                st.session_state.questions[current_index]["transcribed"] = True
                st.write(f"Transcription: {transcript}")

        # 🔹 **Navigation Buttons**
        if st.button("Next Question") and current_index < len(st.session_state.questions) - 1:
            st.session_state.current_question_index += 1
        elif st.session_state.current_question_index == len(st.session_state.questions) - 1:
            st.success("All questions answered. Preparing analysis...")

