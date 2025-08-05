import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
from datetime import datetime, timedelta
import os
from email_validator import validate_email as email_validate, EmailNotValidError
from dotenv import load_dotenv
import config
import pdfkit
import tempfile
import io
import weasyprint

# Load environment variables
load_dotenv()

# Function to get configuration from Streamlit secrets or environment variables
def get_config_value(key, default=None):
    """Get configuration value from Streamlit secrets or environment variables"""
    try:
        # Try to get from Streamlit secrets first
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
        # Fall back to environment variables
        return os.getenv(key, default)
    except:
        return os.getenv(key, default)

def get_email_config():
    """Get email configuration from secrets or environment"""
    try:
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            return {
                'smtp_server': st.secrets['email']['smtp_server'],
                'smtp_port': int(st.secrets['email']['smtp_port']),
                'sender_email': st.secrets['email']['sender_email'],
                'sender_password': st.secrets['email']['sender_password']
            }
        else:
            return {
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'sender_email': os.getenv('SENDER_EMAIL', ''),
                'sender_password': os.getenv('SENDER_PASSWORD', '')
            }
    except:
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': ''
        }

# Page configuration
st.set_page_config(
    page_title="Rapid Innovation - Onboarding Automation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Force white text for better visibility on dark theme */
    .stApp {
        color: #ffffff !important;
    }

    /* Main content area styling */
    .main .block-container {
        color: #ffffff !important;
    }

    /* Form labels and text */
    .stTextInput label, .stSelectbox label, .stDateInput label,
    .stNumberInput label, .stTextArea label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* Form input fields */
    .stTextInput input, .stSelectbox select, .stDateInput input,
    .stNumberInput input, .stTextArea textarea {
        color: #262730 !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
    }

    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2,
    .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMarkdown li, .stMarkdown div {
        color: #ffffff !important;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f0f2f6 !important;
    }

    .css-1d391kg .stSelectbox label {
        color: #ffffff !important;
    }

    /* Button styling */
    .stButton button {
        background-color: #1e3c72 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }

    .stButton button:hover {
        background-color: #2a5298 !important;
        color: white !important;
    }

    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
    }

    .main-header h1, .main-header p {
        color: white !important;
    }

    .section-header {
        background: #f0f2f6;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 4px solid #1e3c72;
        margin: 1rem 0;
        color: #262730 !important;
    }

    .section-header h2 {
        color: #1e3c72 !important;
    }

    .section-header * {
        color: #262730 !important;
    }

    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724 !important;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24 !important;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        color: #262730 !important;
        background-color: #f0f2f6 !important;
    }

    .streamlit-expanderContent {
        color: #262730 !important;
        background-color: white !important;
    }

    /* Table styling */
    .stDataFrame {
        color: #262730 !important;
    }

    /* Warning and info boxes */
    .stAlert {
        color: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🚀 Rapid Innovation - Onboarding Automation System</h1>
    <p>Streamline your employee onboarding process with automated document generation and email delivery</p>
</div>
""", unsafe_allow_html=True)

# Email validation function using email-validator
def validate_email(email):
    try:
        # Validate and get info about the email
        email_validate(email)
        return True
    except EmailNotValidError:
        return False

# Load email configuration from environment variables
def load_email_config():
    return {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'sender_email': os.getenv('DEFAULT_SENDER_EMAIL', ''),
        'sender_password': os.getenv('SMTP_PASSWORD', ''),
        'sender_name': os.getenv('DEFAULT_SENDER_NAME', 'Rapid Innovation HR'),
        'configured': bool(os.getenv('SMTP_SERVER') and os.getenv('SMTP_PASSWORD'))
    }

def get_base64_image(image_path):
    """Convert image to base64 string"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""  # Return empty string if image not found

def convert_html_to_pdf(html_content):
    """Convert HTML content to PDF bytes"""
    # Try pdfkit first (requires wkhtmltopdf)
    try:
        # Configure pdfkit options for better PDF output
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }

        # Convert HTML to PDF
        pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        return pdf_bytes
    except Exception as e:
        st.warning(f"pdfkit failed: {str(e)}. Trying weasyprint as fallback...")

        # Fallback to weasyprint
        try:
            html_doc = weasyprint.HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf()
            return pdf_bytes
        except Exception as e2:
            st.error(f"Both PDF conversion methods failed. pdfkit: {str(e)}, weasyprint: {str(e2)}")
            return None

def generate_offer_letter(offer_type, name, position, start_date, ctc=None):
    """Generate HTML offer letter based on type"""

    # Base64 encode images
    header_img = get_base64_image(config.HEADER_IMAGE_PATH)
    footer_img = get_base64_image(config.FOOTER_IMAGE_PATH)
    signature_img = get_base64_image(config.SIGNATURE_IMAGE_PATH)

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                margin: 20px;
                @top-left {{
                    content: element(header);
                }}
                @bottom-center {{
                    content: element(footer);
                }}
            }}
            body {{
                font-family: {config.DOCUMENT_STYLES['font_family']};
                margin: 0;
                padding: 20px;
                font-size: 12px;
            }}
            .header {{
                text-align: left;
                margin-bottom: 30px;
                position: running(header);
            }}
            .content {{
                margin: 20px 0;
                line-height: {config.DOCUMENT_STYLES['line_height']};
            }}
            .page-break {{ page-break-before: always; }}
            .signature {{
                margin-top: 50px;
                text-align: left;
                page-break-inside: avoid;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                position: running(footer);
                width: 100%;
            }}
            h1, h2 {{ color: {config.DOCUMENT_STYLES['primary_color']}; text-align: center; }}
            .terms {{ margin: 20px 0; }}
            .terms li {{ margin: 10px 0; }}
            .acceptance-section {{
                margin-top: 80px;
                page-break-inside: avoid;
            }}
            .signature-line {{
                border-bottom: 1px solid #000;
                width: 200px;
                margin: 20px 0;
                height: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="data:image/png;base64,{header_img}" style="max-width: 200px; height: auto;">
        </div>

        <div class="content">
            <h2>OFFER LETTER</h2>
            <p><strong>Date:</strong> {datetime.now().strftime('%d %B %Y')}</p>

            <p><strong>Dear {name},</strong></p>

            <p>We are pleased to offer you the position of <strong>{position}</strong> at {config.COMPANY_NAME}, starting on {start_date.strftime('%d %B %Y')}.</p>

            {"<p><strong>Annual CTC:</strong> ₹{:,}</p>".format(ctc) if ctc else ""}

            <div class="terms">
                <h3>Terms and Conditions:</h3>
                <ul>
                    <li>This offer is contingent upon successful completion of background verification and reference checks.</li>
                    <li>You will be required to sign our standard employment agreement and confidentiality agreement.</li>
                    <li>Your employment will be subject to our company policies and procedures.</li>
                    <li>This position includes standard company benefits as per our employee handbook.</li>
                    <li>Probation period: {config.DEFAULT_PROBATION_PERIOD}</li>
                    <li>Notice period: {config.DEFAULT_NOTICE_PERIOD_CONFIRMED} after confirmation</li>
                    <li>You will be entitled to leaves as per company policy</li>
                    <li>All company policies and guidelines must be followed</li>
                </ul>
            </div>

            <div class="page-break"></div>

            <p>Please confirm your acceptance of this offer by signing and returning this letter by {(datetime.now() + timedelta(days=7)).strftime('%d %B %Y')}.</p>

            <p>We look forward to working with you and welcome you to the {config.COMPANY_NAME} family!</p>

            <div class="acceptance-section">
                <p><strong>I HAVE READ THIS OFFER CAREFULLY AND UNDERSTAND ITS TERMS. I HAVE COMPLETELY FILLED OUT THE EXHIBIT A TO THIS OFFER.</strong></p>

                <p><strong>Dated:</strong></p>
                <div class="signature-line"></div>
                <p>(Signature of Employee)<br>({name})</p>

                <p style="margin-top: 40px;"><strong>ACCEPTED AND AGREED TO:</strong></p>
                <p>{config.COMPANY_NAME}</p>
            </div>
        </div>

        <div class="signature">
            <img src="data:image/png;base64,{signature_img}" style="max-width: 120px; height: auto;">
            <p><strong>{config.HR_MANAGER_NAME}</strong><br>
            {config.HR_MANAGER_TITLE}</p>
        </div>

        <div class="footer">
            <img src="data:image/png;base64,{footer_img}" style="max-width: 100%; height: auto;">
        </div>
    </body>
    </html>
    """

    return html_template

def generate_experience_letter(employee_name, position, start_date, end_date, letter_type="standard"):
    """Generate HTML experience letter or internship certificate"""

    # Base64 encode images
    header_img = get_base64_image(config.HEADER_IMAGE_PATH)
    footer_img = get_base64_image(config.FOOTER_IMAGE_PATH)
    signature_img = get_base64_image(config.SIGNATURE_IMAGE_PATH)

    # Calculate duration
    duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    # Determine pronouns based on title in employee_name
    if employee_name.startswith("Mr."):
        pronouns = {"he_she": "He", "his_her": "his", "his_her_cap": "His", "him_her": "him"}
        clean_name = employee_name  # Keep Mr. in the name
    elif employee_name.startswith("Ms."):
        pronouns = {"he_she": "She", "his_her": "her", "his_her_cap": "Her", "him_her": "her"}
        clean_name = employee_name  # Keep Ms. in the name
    else:
        # Fallback to neutral
        pronouns = {"he_she": "They", "his_her": "their", "his_her_cap": "Their", "him_her": "them"}
        clean_name = employee_name

    if letter_type == "internship":
        # Internship Certificate
        content = f"""
        <h3 style="text-align: center; margin: 40px 0; font-weight: bold;">To Whom It May Concern</h3>

        <p style="margin: 30px 0; line-height: 1.8;">This letter is to certify that <strong>{clean_name}</strong> has completed {pronouns['his_her']} internship with Rapid Innovation. {pronouns['his_her_cap']} internship tenure was from <strong>{start_date.strftime('%B %d, %Y')}</strong> to <strong>{end_date.strftime('%B %d, %Y')}</strong>. {pronouns['he_she']} was working with us as an <strong>{position}</strong> and was actively & diligently involved in the projects and tasks assigned to {pronouns['him_her']}.</p>

        <p style="margin: 30px 0; line-height: 1.8;">During this time, we found {pronouns['him_her']} to be punctual and hardworking.</p>

        <p style="margin: 30px 0; line-height: 1.8;">We wish {pronouns['him_her']} a bright future.</p>

        <p style="margin-top: 60px;">Sincerely,</p>
        """
    elif letter_type == "dues_not_settled":
        # Experience Letter - Dues Not Settled
        content = f"""
        <h2 style="text-align: center; margin: 40px 0; font-weight: bold;">EXPERIENCE - CERTIFICATE</h2>
        <h3 style="text-align: center; margin: 20px 0; font-weight: bold;">TO WHOMSOEVER IT MAY CONCERN</h3>

        <p style="margin: 30px 0; line-height: 1.8;">This is to certify that <strong>{clean_name}</strong> worked as a <strong>{position}</strong> with Rapid Innovation from <strong>{start_date.strftime('%B %d, %Y')}</strong> to <strong>{end_date.strftime('%B %d, %Y')}</strong>.</p>

        <p style="margin: 30px 0; line-height: 1.8;">During {pronouns['his_her']} employment with Rapid Innovation, we found {pronouns['his_her']} performance to be satisfactory. However, there are pending dues to be settled.</p>

        <p style="margin: 30px 0; line-height: 1.8;">We wish {pronouns['him_her']} success in {pronouns['his_her']} future endeavors.</p>

        <p style="margin-top: 60px;">Sincerely,</p>
        """
    else:
        # Standard Experience Letter
        content = f"""
        <h2 style="text-align: center; margin: 40px 0; font-weight: bold;">EXPERIENCE - CERTIFICATE</h2>
        <h3 style="text-align: center; margin: 20px 0; font-weight: bold;">TO WHOMSOEVER IT MAY CONCERN</h3>

        <p style="margin: 30px 0; line-height: 1.8;">This is to certify that <strong>{clean_name}</strong> worked as a <strong>{position}</strong> with Rapid Innovation from <strong>{start_date.strftime('%B %d, %Y')}</strong> to <strong>{end_date.strftime('%B %d, %Y')}</strong>.</p>

        <p style="margin: 30px 0; line-height: 1.8;">During {pronouns['his_her']} employment with Rapid Innovation, we found {pronouns['his_her']} performance to be satisfactory. All dues are settled.</p>

        <p style="margin: 30px 0; line-height: 1.8;">We wish {pronouns['him_her']} success in {pronouns['his_her']} future endeavors.</p>

        <p style="margin-top: 60px;">Sincerely,</p>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                margin: 40px 40px 280px 40px;
                @bottom-center {{
                    content: element(footer);
                }}
            }}
            body {{
                font-family: {config.DOCUMENT_STYLES['font_family']};
                margin: 0;
                padding: 0;
                font-size: 14px;
                line-height: 1.6;
                color: #333;
                min-height: 100vh;
            }}
            .page-content {{
                padding: 40px;
                padding-bottom: 280px;
            }}
            .header {{
                text-align: left;
                margin-bottom: 40px;
            }}
            .name-date {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin: 30px 0 50px 0;
                font-size: 14px;
            }}
            .employee-name {{
                text-align: left;
                font-weight: bold;
            }}
            .document-date {{
                text-align: right;
            }}
            .content {{
                margin: 40px 0;
                text-align: justify;
            }}
            .signature {{
                margin-top: 80px;
                text-align: left;
                page-break-inside: avoid;
            }}
            .footer {{
                text-align: center;
                position: running(footer);
                width: 100%;
                margin-top: 50px;
            }}
            h2 {{
                color: #1e3c72;
                font-weight: bold;
                font-size: 18px;
                margin: 40px 0 20px 0;
            }}
            h3 {{
                color: #1e3c72;
                font-weight: bold;
                font-size: 14px;
                margin: 20px 0 30px 0;
            }}
            p {{
                margin: 20px 0;
                text-align: justify;
                font-size: 14px;
                line-height: 1.8;
            }}
        </style>
    </head>
    <body>
        <div class="page-content">
            <div class="header">
                <img src="data:image/png;base64,{header_img}" style="max-width: 150px; height: auto;">
            </div>

            <div class="name-date">
                <div class="employee-name">{employee_name}</div>
                <div class="document-date">{datetime.now().strftime('%d %B %Y')}</div>
            </div>

            <div class="content">
                {content}
            </div>

            <div class="signature">
                <img src="data:image/png;base64,{signature_img}" style="max-width: 120px; height: auto;">
                <p><strong>Aarushi Sharma</strong><br>
                Assistant Manager HR</p>
            </div>
        </div>

        <div class="footer">
            <img src="data:image/png;base64,{footer_img}" style="max-width: 100%; height: auto;">
        </div>
    </body>
    </html>
    """

    return html_template

def convert_text_to_html(processed_content):
    """Convert plain text appointment letter content to HTML with proper formatting"""
    html_content = ""
    lines = processed_content.split('\n')

    in_bullet_list = False
    in_numbered_list = False

    for i, line in enumerate(lines):
        line = line.strip()

        # Skip the first line (name and date) as it will be handled separately
        if i == 0:
            continue

        if not line:
            # Close any open lists before adding line break
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += "<br>"
            continue

        # Handle different types of content
        if line.startswith("●"):
            # Start bullet list if not already in one
            if not in_bullet_list:
                if in_numbered_list:
                    html_content += "</ol>"
                    in_numbered_list = False
                html_content += "<ul>"
                in_bullet_list = True
            html_content += f"<li>{line[1:].strip()}</li>"

        elif line == "Confidential":
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f'<p class="confidential">{line}</p>'

        elif line.startswith("Subject:"):
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<p><strong>{line}</strong></p>"

        elif line.startswith("Dear "):
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<p>{line}</p>"

        elif "TERMS AND CONDITIONS OF EMPLOYMENT" in line:
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<h3>{line}</h3>"

        elif "EMPLOYEE PROPRIETARY INFORMATION" in line or "NON-COMPETITION AND NON-SOLICITATION AGREEMENT" in line:
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<h3>{line}</h3>"

        elif line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.", "11.", "12.", "13.")):
            # Handle numbered sections
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if not in_numbered_list:
                html_content += "<ol>"
                in_numbered_list = True
            # Extract the content after the number
            content = line.split(".", 1)[1].strip() if "." in line else line
            html_content += f"<li><strong>{content}</strong></li>"

        elif (line.endswith(":") and len(line) < 80) or line.isupper():
            # Section headers
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<h4>{line}</h4>"

        elif line.startswith("(") and line.endswith(")"):
            # Signature lines
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<p style='text-align: center;'>{line}</p>"

        elif "ACCEPTED AND AGREED TO:" in line or "Rapid Innovation" in line or "Assistant Manager HR" in line:
            # Signature section
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<p style='text-align: center;'><strong>{line}</strong></p>"

        else:
            # Regular paragraphs
            if in_bullet_list:
                html_content += "</ul>"
                in_bullet_list = False
            if in_numbered_list:
                html_content += "</ol>"
                in_numbered_list = False
            html_content += f"<p>{line}</p>"

    # Close any remaining open lists
    if in_bullet_list:
        html_content += "</ul>"
    if in_numbered_list:
        html_content += "</ol>"

    return html_content

def generate_offer_letter_with_salary(offer_type, candidate_name, position, start_date, salary_data=None):
    """Generate offer letter with detailed salary table for full-time employees"""

    # Base64 encode images
    header_img = get_base64_image(config.HEADER_IMAGE_PATH)
    footer_img = get_base64_image(config.FOOTER_IMAGE_PATH)
    signature_img = get_base64_image(config.SIGNATURE_IMAGE_PATH)

    # Generate salary table HTML if salary data is provided
    salary_table_html = ""
    if salary_data and offer_type == "Full-time Employee":
        salary_table_html = f"""
        <div style="margin: 20px 0;">
            <h3 style="text-align: center; color: #1e3c72; margin-bottom: 15px;">COMPENSATION DETAILS (SALARY AND APPLICABLE BENEFITS)</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 11px;">
                <tr style="background-color: #f8f9fa;">
                    <td style="border: 1px solid #333; padding: 8px; font-weight: bold;">Employee Name</td>
                    <td style="border: 1px solid #333; padding: 8px;">{candidate_name}</td>
                    <td style="border: 1px solid #333; padding: 8px;"></td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="border: 1px solid #333; padding: 8px; font-weight: bold;">Designation</td>
                    <td style="border: 1px solid #333; padding: 8px;">{position}</td>
                    <td style="border: 1px solid #333; padding: 8px;"></td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="border: 1px solid #333; padding: 8px; font-weight: bold;">Date of Joining</td>
                    <td style="border: 1px solid #333; padding: 8px;">{start_date.strftime('%d %B %Y')}</td>
                    <td style="border: 1px solid #333; padding: 8px;"></td>
                </tr>
                <tr style="background-color: #e9ecef;">
                    <td style="border: 1px solid #333; padding: 8px; font-weight: bold;">Particulars</td>
                    <td style="border: 1px solid #333; padding: 8px; font-weight: bold; text-align: center;">Monthly</td>
                    <td style="border: 1px solid #333; padding: 8px; font-weight: bold; text-align: center;">Annual</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">Basic Salary</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['basic_salary_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['basic_salary_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">HRA</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['hra_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['hra_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">Special Allowance</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['special_allowance_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['special_allowance_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">Medical Allowance</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['medical_allowance_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['medical_allowance_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">Books & Periodical</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['books_periodical_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['books_periodical_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">Health Club Facility</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['health_club_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['health_club_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">Internet & Telephone</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['internet_telephone_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['internet_telephone_annual']:,}</td>
                </tr>
                <tr style="background-color: #e9ecef; font-weight: bold;">
                    <td style="border: 1px solid #333; padding: 8px;">Gross CTC</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['gross_ctc_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['gross_ctc_annual']:,}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #333; padding: 8px;">PF Employer Contribution</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['pf_contribution_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['pf_contribution_annual']:,}</td>
                </tr>
                <tr style="background-color: #d4edda; font-weight: bold;">
                    <td style="border: 1px solid #333; padding: 8px;">Total CTC</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['total_ctc_monthly']:,}</td>
                    <td style="border: 1px solid #333; padding: 8px; text-align: right;">{salary_data['total_ctc_annual']:,}</td>
                </tr>
            </table>
        </div>
        """

    # Generate offer letter content based on type
    if offer_type == "Intern":
        content = f"""
        <p style="text-align: right; margin-bottom: 20px;"><strong>Date: {start_date.strftime('%d %B %Y')}</strong></p>

        <h2 style="text-align: center; color: #1e3c72; margin: 30px 0;">Internship Letter</h2>

        <p>Dear {candidate_name},</p>

        <p>With reference to your application and subsequent discussion/interview, we are pleased to offer you the position of <strong>"{position}" Intern</strong> at Rapid Innovation.</p>

        <p>Your internship will start from <strong>{start_date.strftime('%d %B %Y')}</strong> or on a mutually agreed date. This internship is a remote opportunity.</p>

        <p>We are confident that you will be able to make a significant contribution to the success of our Company. Please ensure that you have a stable network connection and uninterrupted power supply at your place. This position is designated as remote until further notified by the management.</p>

        <p>Please sign and share the scanned copy of this letter and return it to the HR Department to indicate your acceptance of this offer.</p>

        <p>Sincerely,</p>
        """
    elif offer_type == "Full-time Employee":
        # Page 1 content only
        content = f"""
        <p style="text-align: right; margin-bottom: 20px;"><strong>Date: {start_date.strftime('%d %B %Y')}</strong></p>

        <h2 style="text-align: center; color: #1e3c72; margin: 30px 0;">Offer Letter</h2>

        <p>Dear {candidate_name},</p>

        <p>With reference to your application and subsequent discussion/interview, we are pleased to offer you the position of <strong>"{position}"</strong> at Rapid Innovation.</p>

        <p>Your full time employment will start from <strong>{start_date.strftime('%d %B %Y')}</strong> or on before Wednesday. This offer is subjected to reference check, as provided by you.</p>

        <p>In recognition of your contributions, we are pleased to inform you that your annual CTC will be <strong>Rs. {salary_data['total_ctc_annual']:,}/-</strong> (Rupees {number_to_words(salary_data['total_ctc_annual'])} Only) per annum.</p>

        <p>Please note that we are attaching the pay structure with this offer letter.</p>
        """

        # Page 2 content
        page2_content = f"""
        {salary_table_html}

        <p><strong>Please Note:</strong></p>
        <p>The Company shall withhold from any amounts payable to you such taxes as may be required to withhold pursuant to applicable laws or regulation. In case of any under-withholding caused due to any wrong declaration by you, you shall be solely responsible to pay the necessary tax and any interest/penalty thereon.</p>

        <p>For,<br>Rapid Innovation.</p>

        <p>You will be on probation for a period of (3) Three Months from the date of your joining. Your performance will be assessed for confirmation on your parameters as per required for the time assessment.</p>

        <p>We are confident that you will be able to make a significant contribution to the success of our Company. Please ensure that you have a stable network connection and uninterrupted power supply at your place. This position is designated as remote until further notified by the management.</p>

        <p>Please sign and share the scanned copy of this letter and return it to the HR Department to indicate your acceptance of this offer.</p>

        <p>Sincerely,</p>
        """
    else:  # Contractor
        content = f"""
        <p style="text-align: right; margin-bottom: 20px;"><strong>Date: {start_date.strftime('%d %B %Y')}</strong></p>

        <h2 style="text-align: center; color: #1e3c72; margin: 30px 0;">Contract Letter</h2>

        <p>Dear {candidate_name},</p>

        <p>With reference to your application and subsequent discussion/interview, we are pleased to offer you the position of <strong>"{position}" Contractor</strong> at Rapid Innovation.</p>

        <p>Your contract will start from <strong>{start_date.strftime('%d %B %Y')}</strong> or on a mutually agreed date. This contract is a remote opportunity.</p>

        <p>We are confident that you will be able to make a significant contribution to the success of our Company. Please ensure that you have a stable network connection and uninterrupted power supply at your place. This position is designated as remote until further notified by the management.</p>

        <p>Please sign and share the scanned copy of this letter and return it to the HR Department to indicate your acceptance of this offer.</p>

        <p>Sincerely,</p>
        """

    # Create different templates based on offer type
    if offer_type == "Full-time Employee":
        # Full-time offer letter template with clean format (same as internship)
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    margin: 40px 40px 120px 40px;
                }}
                body {{
                    font-family: {config.DOCUMENT_STYLES['font_family']};
                    margin: 0;
                    padding: 0;
                    line-height: {config.DOCUMENT_STYLES['line_height']};
                    font-size: 12px;
                    color: #333;
                }}
                .page-content {{
                    padding: 20px;
                    padding-bottom: 120px;
                    min-height: calc(100vh - 240px);
                }}
                .header {{ text-align: left; margin-bottom: 30px; }}
                .content {{ margin: 20px 0; }}
                .signature {{ margin-top: 50px; text-align: left; page-break-inside: avoid; }}
                .footer {{
                    text-align: center;
                    width: 100%;
                    margin-top: 20px;
                    page-break-inside: avoid;
                }}
                .footer-bottom {{
                    text-align: center;
                    width: 100%;
                    margin-top: 180px;
                    page-break-inside: avoid;
                }}
                h1, h2, h3 {{ color: {config.DOCUMENT_STYLES['primary_color']}; }}
                p {{ text-align: justify; margin: 8px 0; line-height: 1.4; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                td {{ border: 1px solid #333; padding: 8px; }}
            </style>
        </head>
        <body>
            <!-- Page 1 -->
            <div class="page-content">
                <div class="header">
                    <img src="data:image/png;base64,{header_img}" style="max-width: 150px; height: auto;">
                </div>

                <div class="content">
                    {content}
                </div>

                <div class="signature">
                    <img src="data:image/png;base64,{signature_img}" style="max-width: 80px; height: auto;">
                    <p><strong>Aarushi Sharma</strong><br>
                    Assistant Manager HR</p>
                    <br><br>
                    <p style="text-align: right;"><strong>Accepted By</strong><br>
                    {candidate_name}</p>
                </div>

                <div class="footer-bottom" style="margin-top: 470px;">
                    <img src="data:image/png;base64,{footer_img}" style="max-width: 100%; height: auto;">
                </div>
            </div>

            <!-- Page 2 -->
            <div style="page-break-before: always;"></div>
            <div class="page-content">
                <div class="header">
                    <img src="data:image/png;base64,{header_img}" style="max-width: 150px; height: auto;">
                </div>

                <div class="content">
                    {page2_content}
                </div>

                <div class="signature">
                    <img src="data:image/png;base64,{signature_img}" style="max-width: 80px; height: auto;">
                    <p><strong>Aarushi Sharma</strong><br>
                    Assistant Manager HR</p>
                    <br><br>
                    <p style="text-align: right;"><strong>Accepted By</strong><br>
                    {candidate_name}</p>
                </div>

                <div class="footer">
                    <img src="data:image/png;base64,{footer_img}" style="max-width: 100%; height: auto;">
                </div>
            </div>
        </body>
        </html>
        """
    else:
        # Internship letter template (existing clean format)
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    margin: 40px 40px 500px 40px;
                    @bottom-center {{
                        content: element(footer);
                    }}
                }}
                body {{
                    font-family: {config.DOCUMENT_STYLES['font_family']};
                    margin: 0;
                    padding: 0;
                    line-height: {config.DOCUMENT_STYLES['line_height']};
                    font-size: 12px;
                    color: #333;
                    min-height: 100vh;
                    position: relative;
                }}
                .page-content {{
                    padding: 20px;
                    padding-bottom: 500px;
                }}
                .header {{ text-align: left; margin-bottom: 30px; }}
                .content {{ margin: 20px 0; }}
                .signature {{ margin-top: 50px; text-align: left; page-break-inside: avoid; }}
                .footer {{
                    text-align: center;
                    position: running(footer);
                    width: 100%;
                    margin-top: 50px;
                }}
                h1, h2, h3 {{ color: {config.DOCUMENT_STYLES['primary_color']}; }}
                p {{ text-align: justify; margin: 8px 0; line-height: 1.4; }}
                table {{ border-collapse: collapse; width: 100%; }}
                td {{ border: 1px solid #333; padding: 8px; }}
            </style>
        </head>
        <body>
            <div class="page-content">
                <div class="header">
                    <img src="data:image/png;base64,{header_img}" style="max-width: 200px; height: auto;">
                </div>

                <div class="content">
                    {content}
                </div>

                <div class="signature">
                    <img src="data:image/png;base64,{signature_img}" style="max-width: 80px; height: auto;">
                    <p><strong>Aarushi Sharma</strong><br>
                    Assistant Manager HR</p>
                    <br><br>
                    <p style="text-align: right;"><strong>Accepted By</strong><br>
                    {candidate_name}</p>
                </div>
            </div>

            <div class="footer">
                <img src="data:image/png;base64,{footer_img}" style="max-width: 100%; height: auto;">
            </div>
        </body>
        </html>
        """

    return html_template

def number_to_words(number):
    """Convert number to words (simplified version)"""
    # This is a simplified version - you might want to use a library like num2words for production
    if number >= 100000:
        lakhs = number // 100000
        remainder = number % 100000
        if remainder == 0:
            return f"{lakhs} Lakh"
        else:
            return f"{lakhs} Lakh {remainder:,}"
    else:
        return f"{number:,}"

def generate_appointment_letter(name, position, joining_date):
    """Generate HTML appointment letter with content from appointment_letter.txt"""

    # Read the appointment letter template
    try:
        with open('appointment_letter.txt', 'r', encoding='utf-8') as file:
            letter_content = file.read()
    except FileNotFoundError:
        st.error("appointment_letter.txt file not found!")
        return ""

    # Base64 encode images
    header_img = get_base64_image(config.HEADER_IMAGE_PATH)
    footer_img = get_base64_image(config.FOOTER_IMAGE_PATH)
    signature_img = get_base64_image(config.SIGNATURE_IMAGE_PATH)

    # Process the letter content to replace placeholders
    processed_content = letter_content.replace("Naman Nagi", name)
    processed_content = processed_content.replace("Associate Engineer", position)
    processed_content = processed_content.replace("18th June 2025", joining_date.strftime('%d %B %Y'))

    # Convert text to HTML with proper formatting
    html_content = convert_text_to_html(processed_content)

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: {config.DOCUMENT_STYLES['font_family']};
                margin: 0;
                padding: 20px;
                line-height: {config.DOCUMENT_STYLES['line_height']};
                font-size: 12px;
                color: #333;
            }}
            .header {{ text-align: left; margin-bottom: 30px; }}
            .content {{ margin: 20px 0; }}
            .signature {{ margin-top: 50px; text-align: left; }}
            .footer {{ text-align: center; margin-top: 50px; }}
            h1, h2, h3 {{
                color: {config.DOCUMENT_STYLES['primary_color']};
                margin-top: 20px;
                margin-bottom: 10px;
                font-weight: bold;
            }}
            h4 {{
                color: {config.DOCUMENT_STYLES['primary_color']};
                margin-top: 15px;
                margin-bottom: 8px;
                font-weight: bold;
                font-size: 13px;
            }}
            .confidential {{
                text-align: right;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .date-header {{
                text-align: right;
                margin-bottom: 20px;
            }}
            ul {{
                margin: 10px 0;
                padding-left: 25px;
                list-style-type: disc;
            }}
            ol {{
                margin: 10px 0;
                padding-left: 25px;
                list-style-type: decimal;
            }}
            li {{
                margin: 8px 0;
                text-align: justify;
                line-height: 1.4;
            }}
            p {{
                text-align: justify;
                margin: 8px 0;
                line-height: 1.4;
            }}
            .signature-section {{
                margin-top: 40px;
                text-align: left;
            }}
            .signature-line {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="data:image/png;base64,{header_img}" style="max-width: 150px; height: auto;">
        </div>

        <div class="content">
            {html_content}
        </div>

        <div class="signature">
            <img src="data:image/png;base64,{signature_img}" style="max-width: 120px; height: auto;">
            <p><strong>Aarushi Sharma</strong><br>
            Assistant Manager HR</p>
            <br><br>
            <p style="text-align: right;"><strong>Accepted By</strong><br>
            {name}</p>
        </div>

        <div class="footer">
            <img src="data:image/png;base64,{footer_img}" style="max-width: 100%; height: auto;">
        </div>
    </body>
    </html>
    """

    return html_template

# Email sending function
def send_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email, cc_emails, subject, body, attachment_data=None, attachment_name=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))

        if attachment_data and attachment_name:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_name}'
            )
            msg.attach(part)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        recipients = [recipient_email] + (cc_emails if cc_emails else [])
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose Process", [
    "🏠 Home",
    "📧 Email Configuration",
    "📝 Phase 1: Initial Documents",
    "📄 Phase 2: Offer Letters",
    "📋 Phase 3: Appointment Letters",
    "🎯 Phase 4: Welcome & Onboarding",
    "🔍 Phase 5: Background Verification",
    "🚪 Phase 6: Exit Process"
])

# Email configuration in session state
if 'email_config' not in st.session_state:
    # Try to load from Streamlit secrets or environment variables
    try:
        email_config = get_email_config()
        email_config['configured'] = bool(email_config['sender_email'] and email_config['sender_password'])
        email_config['sender_name'] = get_config_value('SENDER_NAME', 'Rapid Innovation HR')
        st.session_state.email_config = email_config
    except:
        # Fallback to old method
        env_config = load_email_config()
        st.session_state.email_config = env_config

if page == "🏠 Home":
    st.markdown("""
    <div class="section-header">
        <h2>Welcome to Rapid Innovation Onboarding System</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    This comprehensive onboarding automation system helps you manage the complete employee onboarding process:
    
    ### 🔧 **Phase 1: Pre-Joining Formalities**
    - Initial document request emails
    - Automated email templates for interns and full-time employees
    
    ### 📄 **Phase 2: Offer Letter Generation**
    - Professional offer letters for interns, employees, and contractors
    - Customizable templates with company branding
    
    ### 📋 **Phase 3: Appointment Letters**
    - Formal appointment letters with terms and conditions
    - Legal agreements and NDAs
    
    ### 🎯 **Phase 4: Welcome & System Enrollment**
    - Welcome emails with joining forms
    - Platform enrollment instructions
    
    ### 🔍 **Phase 5: Background Verification**
    - Automated BGV emails to previous employers
    - Verification forms and tracking

    ### 🚪 **Phase 6: Exit Process**
    - Manager confirmation and exit communication
    - Asset return and access management
    - Experience letters and internship certificates

    ### ✨ **Key Features:**
    - 📧 Direct email sending with SMTP integration
    - 📱 Email validation and verification
    - 🎨 Professional document templates
    - 📎 Automatic PDF generation and attachment
    - 🔒 Secure email configuration
    """)

elif page == "📧 Email Configuration":
    st.markdown("""
    <div class="section-header">
        <h2>📧 Email Configuration</h2>
    </div>
    """, unsafe_allow_html=True)

    # Check if configuration is loaded from secrets or environment
    if st.session_state.email_config['configured']:
        # Check if loaded from Streamlit secrets
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            st.success("✅ Email configuration loaded from Streamlit Cloud secrets!")
        else:
            st.success("✅ Email configuration loaded from environment variables!")

        st.info(f"**Sender Email:** {st.session_state.email_config['sender_email']}")
        st.info(f"**SMTP Server:** {st.session_state.email_config['smtp_server']}:{st.session_state.email_config['smtp_port']}")
    else:
        st.info("Configure your email settings to enable automatic email sending functionality.")

    with st.form("email_config_form"):
        col1, col2 = st.columns(2)

        with col1:
            smtp_server = st.text_input("SMTP Server", value=st.session_state.email_config['smtp_server'],
                                      placeholder="smtp.gmail.com")
            sender_email = st.text_input("Sender Email", value=st.session_state.email_config['sender_email'],
                                       placeholder="hr@rapidinnovation.com")

        with col2:
            smtp_port = st.number_input("SMTP Port", value=st.session_state.email_config['smtp_port'],
                                      min_value=1, max_value=65535)
            sender_password = st.text_input("Email Password", type="password",
                                          value=st.session_state.email_config.get('sender_password', ''),
                                          placeholder="Your email password or app password")

        submitted = st.form_submit_button("💾 Save Configuration")

        if submitted:
            if smtp_server and sender_email and sender_password:
                if validate_email(sender_email):
                    st.session_state.email_config = {
                        'smtp_server': smtp_server,
                        'smtp_port': smtp_port,
                        'sender_email': sender_email,
                        'sender_password': sender_password,
                        'sender_name': st.session_state.email_config.get('sender_name', 'Rapid Innovation HR'),
                        'configured': True
                    }
                    st.markdown('<div class="success-box">✅ Email configuration saved successfully!</div>',
                              unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box">❌ Please enter a valid email address.</div>',
                              unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">❌ Please fill in all required fields.</div>',
                          unsafe_allow_html=True)
    
    if st.session_state.email_config['configured']:
        st.success("✅ Email configuration is active!")
        
        # Test email functionality
        st.markdown("### 🧪 Test Email Configuration")
        test_email = st.text_input("Test Email Address", placeholder="test@example.com")
        
        if st.button("📤 Send Test Email"):
            if test_email and validate_email(test_email):
                success, message = send_email(
                    st.session_state.email_config['smtp_server'],
                    st.session_state.email_config['smtp_port'],
                    st.session_state.email_config['sender_email'],
                    st.session_state.email_config['sender_password'],
                    test_email,
                    [],
                    "Test Email - Rapid Innovation Onboarding System",
                    "<h2>Test Email</h2><p>This is a test email from the Rapid Innovation Onboarding System. If you received this, your email configuration is working correctly!</p>"
                )
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.error("Please enter a valid test email address.")

elif page == "📝 Phase 1: Initial Documents":
    st.markdown("""
    <div class="section-header">
        <h2>📝 Phase 1: Initial Document Request</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.email_config['configured']:
        st.warning("⚠️ Please configure email settings first in the Email Configuration section.")
        st.stop()
    
    # Employee type selection
    employee_type = st.selectbox("Select Employee Type", ["Intern", "Full-time Employee"])
    
    with st.form("initial_docs_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            employee_name = st.text_input("Employee Name*", placeholder="John Doe")
            employee_email = st.text_input("Employee Email*", placeholder="john.doe@email.com")
            position = st.text_input("Position/Designation*", placeholder="Software Engineer")
        
        with col2:
            cc_emails = st.text_area("CC Emails (one per line)", placeholder="hr@rapidinnovation.com\nmanager@rapidinnovation.com")
            
        submitted = st.form_submit_button("📤 Generate & Send Email")
        
        if submitted:
            if employee_name and employee_email and position:
                if validate_email(employee_email):
                    # Parse CC emails
                    cc_list = [email.strip() for email in cc_emails.split('\n') if email.strip() and validate_email(email.strip())]
                    
                    # Generate email content based on employee type
                    if employee_type == "Intern":
                        subject = f'Rapid Innovation - Important Documents Required - "{position}" Intern'
                        body = f"""
                        <html>
                        <body>
                        <p>Hi {employee_name},</p>
                        <p>Greetings from Rapid Innovation!!</p>
                        <p>This is regarding your joining for the "{position}" Intern position at Rapid Innovation.</p>
                        <p>As a part of our Employment Joining process, we would require soft copies of the below-mentioned documents:</p>
                        <ol>
                            <li>Educational Docs (10th, 12th, Graduation & Post Graduation Certificates)</li>
                            <li>ID proofs (Aadhaar card, Passport, Driving license, PAN card)</li>
                            <li>Passport-size photographs</li>
                        </ol>
                        <p>Also, please share your full name and address as per your documents.</p>
                        <p>Feel free to get in touch with me in case of any queries or questions.</p>
                        <br>
                        <p>Thanks & Regards<br>
                        Team HR<br>
                        Rapid Innovation</p>
                        </body>
                        </html>
                        """
                    else:  # Full-time Employee
                        subject = f'Rapid Innovation - Important Documents Required - {position}'
                        body = f"""
                        <html>
                        <body>
                        <p>Hi {employee_name},</p>
                        <p>Greetings from Rapid Innovation!!</p>
                        <p>This is regarding your joining for the "{position}" position at Rapid Innovation.</p>
                        <p>As a part of our Employment Joining process, we would require soft copies of the below-mentioned documents:</p>
                        <ul>
                            <li>Educational Docs (10th, 12th, Graduation & Post Graduation Certificates)</li>
                            <li>ID proofs (Aadhaar card, Passport, Driving license, PAN card)</li>
                            <li>Resignation/relieving letters, the Last three Months of salary slips, Appointment letters, and offer letters from previous organizations.</li>
                            <li>Passport-size photograph</li>
                        </ul>
                        <p>Also, please share your full name and address as per your documents.</p>
                        <p>Feel free to get in touch with me in case of any queries or questions.</p>
                        <br>
                        <p>Thanks & Regards<br>
                        Team HR<br>
                        Rapid Innovation</p>
                        </body>
                        </html>
                        """
                    
                    # Send email
                    success, message = send_email(
                        st.session_state.email_config['smtp_server'],
                        st.session_state.email_config['smtp_port'],
                        st.session_state.email_config['sender_email'],
                        st.session_state.email_config['sender_password'],
                        employee_email,
                        cc_list,
                        subject,
                        body
                    )
                    
                    if success:
                        st.markdown('<div class="success-box">✅ Initial document request email sent successfully!</div>', 
                                  unsafe_allow_html=True)
                        
                        # Show preview
                        with st.expander("📧 Email Preview"):
                            st.markdown(f"**To:** {employee_email}")
                            if cc_list:
                                st.markdown(f"**CC:** {', '.join(cc_list)}")
                            st.markdown(f"**Subject:** {subject}")
                            st.markdown("**Body:**")
                            st.markdown(body, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                else:
                    st.error("Please enter a valid employee email address.")
            else:
                st.error("Please fill in all required fields.")

elif page == "📄 Phase 2: Offer Letters":
    st.markdown("""
    <div class="section-header">
        <h2>📄 Phase 2: Offer Letter Generation</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.email_config['configured']:
        st.warning("⚠️ Please configure email settings first in the Email Configuration section.")
        st.stop()

    # Initialize session state for offer letter data
    if 'offer_letter_data' not in st.session_state:
        st.session_state.offer_letter_data = None
    if 'offer_letter_html' not in st.session_state:
        st.session_state.offer_letter_html = None

    # Offer letter type selection
    offer_type = st.selectbox("Select Offer Type", ["Intern", "Full-time Employee", "Contractor"])

    with st.form("offer_letter_form"):
        st.markdown("### 📝 Basic Information")
        col1, col2 = st.columns(2)

        with col1:
            candidate_name = st.text_input("Candidate Name*", placeholder="John Doe")
            candidate_email = st.text_input("Candidate Email*", placeholder="john.doe@email.com")
            position = st.text_input("Position/Designation*", placeholder="Software Engineer")
            start_date = st.date_input("Start Date*")

        with col2:
            cc_emails = st.text_area("CC Emails (one per line)", placeholder="hr@rapidinnovation.com")

        # Salary Details Section (only for Full-time Employee)
        if offer_type == "Full-time Employee":
            st.markdown("### 💰 Compensation Details")
            st.markdown("*Fill in the salary breakdown table below:*")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Monthly Amounts:**")
                basic_salary_monthly = st.number_input("Basic Salary (Monthly)", min_value=0, value=19934, step=1)
                hra_monthly = st.number_input("HRA (Monthly)", min_value=0, value=9967, step=1)
                special_allowance_monthly = st.number_input("Special Allowance (Monthly)", min_value=0, value=4716, step=1)
                medical_allowance_monthly = st.number_input("Medical Allowance (Monthly)", min_value=0, value=1250, step=1)
                books_periodical_monthly = st.number_input("Books & Periodical (Monthly)", min_value=0, value=500, step=1)
                health_club_monthly = st.number_input("Health Club Facility (Monthly)", min_value=0, value=1000, step=1)
                internet_telephone_monthly = st.number_input("Internet & Telephone (Monthly)", min_value=0, value=2500, step=1)

            with col2:
                st.markdown("**Annual Amounts (Auto-calculated):**")
                basic_salary_annual = basic_salary_monthly * 12
                hra_annual = hra_monthly * 12
                special_allowance_annual = special_allowance_monthly * 12
                medical_allowance_annual = medical_allowance_monthly * 12
                books_periodical_annual = books_periodical_monthly * 12
                health_club_annual = health_club_monthly * 12
                internet_telephone_annual = internet_telephone_monthly * 12

                st.text_input("Basic Salary (Annual)", value=f"{basic_salary_annual:,}", disabled=True)
                st.text_input("HRA (Annual)", value=f"{hra_annual:,}", disabled=True)
                st.text_input("Special Allowance (Annual)", value=f"{special_allowance_annual:,}", disabled=True)
                st.text_input("Medical Allowance (Annual)", value=f"{medical_allowance_annual:,}", disabled=True)
                st.text_input("Books & Periodical (Annual)", value=f"{books_periodical_annual:,}", disabled=True)
                st.text_input("Health Club Facility (Annual)", value=f"{health_club_annual:,}", disabled=True)
                st.text_input("Internet & Telephone (Annual)", value=f"{internet_telephone_annual:,}", disabled=True)

            with col3:
                st.markdown("**Totals & Deductions:**")
                gross_ctc_monthly = (basic_salary_monthly + hra_monthly + special_allowance_monthly +
                                   medical_allowance_monthly + books_periodical_monthly + health_club_monthly +
                                   internet_telephone_monthly)
                gross_ctc_annual = gross_ctc_monthly * 12

                pf_contribution_monthly = st.number_input("PF Employer Contribution (Monthly)", min_value=0, value=1800, step=1)
                pf_contribution_annual = pf_contribution_monthly * 12

                total_ctc_monthly = gross_ctc_monthly + pf_contribution_monthly
                total_ctc_annual = total_ctc_monthly * 12

                st.text_input("Gross CTC (Monthly)", value=f"{gross_ctc_monthly:,}", disabled=True)
                st.text_input("Gross CTC (Annual)", value=f"{gross_ctc_annual:,}", disabled=True)
                st.text_input("PF Contribution (Annual)", value=f"{pf_contribution_annual:,}", disabled=True)
                st.text_input("Total CTC (Monthly)", value=f"{total_ctc_monthly:,}", disabled=True)
                st.text_input("Total CTC (Annual)", value=f"{total_ctc_annual:,}", disabled=True)

        submitted = st.form_submit_button("📄 Generate Offer Letter")

        if submitted:
            if candidate_name and candidate_email and position and start_date:
                if validate_email(candidate_email):
                    # Parse CC emails
                    cc_list = [email.strip() for email in cc_emails.split('\n') if email.strip() and validate_email(email.strip())]

                    # Prepare salary data for full-time employees
                    salary_data = None
                    if offer_type == "Full-time Employee":
                        salary_data = {
                            'basic_salary_monthly': basic_salary_monthly,
                            'basic_salary_annual': basic_salary_annual,
                            'hra_monthly': hra_monthly,
                            'hra_annual': hra_annual,
                            'special_allowance_monthly': special_allowance_monthly,
                            'special_allowance_annual': special_allowance_annual,
                            'medical_allowance_monthly': medical_allowance_monthly,
                            'medical_allowance_annual': medical_allowance_annual,
                            'books_periodical_monthly': books_periodical_monthly,
                            'books_periodical_annual': books_periodical_annual,
                            'health_club_monthly': health_club_monthly,
                            'health_club_annual': health_club_annual,
                            'internet_telephone_monthly': internet_telephone_monthly,
                            'internet_telephone_annual': internet_telephone_annual,
                            'gross_ctc_monthly': gross_ctc_monthly,
                            'gross_ctc_annual': gross_ctc_annual,
                            'pf_contribution_monthly': pf_contribution_monthly,
                            'pf_contribution_annual': pf_contribution_annual,
                            'total_ctc_monthly': total_ctc_monthly,
                            'total_ctc_annual': total_ctc_annual
                        }

                    # Store offer letter data in session state
                    st.session_state.offer_letter_data = {
                        'offer_type': offer_type,
                        'candidate_name': candidate_name,
                        'candidate_email': candidate_email,
                        'position': position,
                        'start_date': start_date,
                        'cc_list': cc_list,
                        'salary_data': salary_data
                    }

                    # Generate offer letter HTML
                    st.session_state.offer_letter_html = generate_offer_letter_with_salary(
                        offer_type, candidate_name, position, start_date, salary_data
                    )

                    st.success("✅ Offer letter generated successfully! Please review below.")
                else:
                    st.error("Please enter a valid candidate email address.")
            else:
                st.error("Please fill in all required fields.")

    # Show preview and edit functionality if letter is generated
    if st.session_state.offer_letter_html and st.session_state.offer_letter_data:
        st.markdown("---")

        # Preview section
        with st.expander("📋 Offer Letter Preview", expanded=True):
            st.markdown("**Preview of your offer letter:**")
            # Display HTML preview in a container
            st.markdown(st.session_state.offer_letter_html, unsafe_allow_html=True)

        # Edit section for salary (only for full-time employees)
        if st.session_state.offer_letter_data['offer_type'] == "Full-time Employee":
            with st.expander("✏️ Edit Salary Details"):
                st.markdown("**Edit the salary breakdown below:**")

                data = st.session_state.offer_letter_data
                salary_data = data['salary_data']

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("**Monthly Amounts:**")
                    new_basic_monthly = st.number_input("Basic Salary (Monthly)", min_value=0, value=salary_data['basic_salary_monthly'], step=1, key="edit_basic")
                    new_hra_monthly = st.number_input("HRA (Monthly)", min_value=0, value=salary_data['hra_monthly'], step=1, key="edit_hra")
                    new_special_monthly = st.number_input("Special Allowance (Monthly)", min_value=0, value=salary_data['special_allowance_monthly'], step=1, key="edit_special")
                    new_medical_monthly = st.number_input("Medical Allowance (Monthly)", min_value=0, value=salary_data['medical_allowance_monthly'], step=1, key="edit_medical")
                    new_books_monthly = st.number_input("Books & Periodical (Monthly)", min_value=0, value=salary_data['books_periodical_monthly'], step=1, key="edit_books")
                    new_health_monthly = st.number_input("Health Club Facility (Monthly)", min_value=0, value=salary_data['health_club_monthly'], step=1, key="edit_health")
                    new_internet_monthly = st.number_input("Internet & Telephone (Monthly)", min_value=0, value=salary_data['internet_telephone_monthly'], step=1, key="edit_internet")
                    new_pf_monthly = st.number_input("PF Employer Contribution (Monthly)", min_value=0, value=salary_data['pf_contribution_monthly'], step=1, key="edit_pf")

                with col2:
                    st.markdown("**Annual Amounts (Auto-calculated):**")
                    new_basic_annual = new_basic_monthly * 12
                    new_hra_annual = new_hra_monthly * 12
                    new_special_annual = new_special_monthly * 12
                    new_medical_annual = new_medical_monthly * 12
                    new_books_annual = new_books_monthly * 12
                    new_health_annual = new_health_monthly * 12
                    new_internet_annual = new_internet_monthly * 12
                    new_pf_annual = new_pf_monthly * 12

                    st.text_input("Basic Salary (Annual)", value=f"{new_basic_annual:,}", disabled=True, key="show_basic_annual")
                    st.text_input("HRA (Annual)", value=f"{new_hra_annual:,}", disabled=True, key="show_hra_annual")
                    st.text_input("Special Allowance (Annual)", value=f"{new_special_annual:,}", disabled=True, key="show_special_annual")
                    st.text_input("Medical Allowance (Annual)", value=f"{new_medical_annual:,}", disabled=True, key="show_medical_annual")
                    st.text_input("Books & Periodical (Annual)", value=f"{new_books_annual:,}", disabled=True, key="show_books_annual")
                    st.text_input("Health Club Facility (Annual)", value=f"{new_health_annual:,}", disabled=True, key="show_health_annual")
                    st.text_input("Internet & Telephone (Annual)", value=f"{new_internet_annual:,}", disabled=True, key="show_internet_annual")
                    st.text_input("PF Contribution (Annual)", value=f"{new_pf_annual:,}", disabled=True, key="show_pf_annual")

                with col3:
                    st.markdown("**Totals:**")
                    new_gross_monthly = (new_basic_monthly + new_hra_monthly + new_special_monthly +
                                       new_medical_monthly + new_books_monthly + new_health_monthly +
                                       new_internet_monthly)
                    new_gross_annual = new_gross_monthly * 12
                    new_total_monthly = new_gross_monthly + new_pf_monthly
                    new_total_annual = new_total_monthly * 12

                    st.text_input("Gross CTC (Monthly)", value=f"{new_gross_monthly:,}", disabled=True, key="show_gross_monthly")
                    st.text_input("Gross CTC (Annual)", value=f"{new_gross_annual:,}", disabled=True, key="show_gross_annual")
                    st.text_input("Total CTC (Monthly)", value=f"{new_total_monthly:,}", disabled=True, key="show_total_monthly")
                    st.text_input("Total CTC (Annual)", value=f"{new_total_annual:,}", disabled=True, key="show_total_annual")

                if st.button("🔄 Update Offer Letter"):
                    # Update salary data
                    updated_salary_data = {
                        'basic_salary_monthly': new_basic_monthly,
                        'basic_salary_annual': new_basic_annual,
                        'hra_monthly': new_hra_monthly,
                        'hra_annual': new_hra_annual,
                        'special_allowance_monthly': new_special_monthly,
                        'special_allowance_annual': new_special_annual,
                        'medical_allowance_monthly': new_medical_monthly,
                        'medical_allowance_annual': new_medical_annual,
                        'books_periodical_monthly': new_books_monthly,
                        'books_periodical_annual': new_books_annual,
                        'health_club_monthly': new_health_monthly,
                        'health_club_annual': new_health_annual,
                        'internet_telephone_monthly': new_internet_monthly,
                        'internet_telephone_annual': new_internet_annual,
                        'gross_ctc_monthly': new_gross_monthly,
                        'gross_ctc_annual': new_gross_annual,
                        'pf_contribution_monthly': new_pf_monthly,
                        'pf_contribution_annual': new_pf_annual,
                        'total_ctc_monthly': new_total_monthly,
                        'total_ctc_annual': new_total_annual
                    }

                    # Update session state
                    st.session_state.offer_letter_data['salary_data'] = updated_salary_data

                    # Regenerate offer letter HTML
                    st.session_state.offer_letter_html = generate_offer_letter_with_salary(
                        data['offer_type'], data['candidate_name'], data['position'],
                        data['start_date'], updated_salary_data
                    )

                    st.success("✅ Offer letter updated successfully!")
                    st.rerun()

        # Download and Send section
        st.markdown("### 📥 Download & Send Options")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Download as PDF"):
                pdf_bytes = convert_html_to_pdf(st.session_state.offer_letter_html)
                if pdf_bytes:
                    data = st.session_state.offer_letter_data
                    pdf_filename = f"{data['offer_type'].lower().replace(' ', '_')}_letter_{data['candidate_name'].replace(' ', '_')}.pdf"
                    st.download_button(
                        label="💾 Download PDF",
                        data=pdf_bytes,
                        file_name=pdf_filename,
                        mime="application/pdf"
                    )
                else:
                    st.error("❌ Failed to generate PDF. Please check if wkhtmltopdf is installed.")

        with col2:
            if st.button("📧 Send Email with PDF"):
                data = st.session_state.offer_letter_data

                # Generate email content based on offer type
                if data['offer_type'] == "Intern":
                    subject = f'Rapid Innovation - Letter of Internship - "{data["position"]}" Intern'
                    email_body = f"""
                    <html>
                    <body>
                    <p>Hello {data['candidate_name']},</p>
                    <p>Greetings from Rapid Innovation!!</p>
                    <p>As discussed, we are pleased to extend the offer to you for the "{data['position']}" Intern position at Rapid Innovation Pvt. Ltd. - Remote, starting on {data['start_date'].strftime('%B %d, %Y')}.</p>
                    <p>PFA the copy of the internship letter for your ready reference. Kindly revert with your acceptance by sending the duly signed copy of the letter.</p>
                    <p>At Rapid Innovation, we provide every possible opportunity for the growth and development of our people, and we hope that you will also contribute to the growth of Rapid Innovation.</p>
                    <p>We look forward to a lasting relationship between us.</p>
                    <p>Best wishes for your new endeavors !!</p>
                    <p>Please feel free to contact us if you have any queries.</p>
                    <br>
                    <p>Regards<br>
                    Team HR<br>
                    Rapid Innovation</p>
                    </body>
                    </html>
                    """
                elif data['offer_type'] == "Full-time Employee":
                    subject = f'Rapid Innovation - Offer letter - {data["position"]}'
                    email_body = f"""
                    <html>
                    <body>
                    <p>Hello {data['candidate_name']},</p>
                    <p>Greetings from Rapid Innovation !!</p>
                    <p>We are pleased to extend the offer to you for the position of "{data['position']}" at Rapid Innovation, starting on or before {data['start_date'].strftime('%B %d, %Y')}.</p>
                    <p>PFA the copy of the offer letter for your ready reference. Kindly revert with your acceptance by sending the duly signed copy of the letter. This opportunity is a permanent remote job.</p>
                    <p>At Rapid Innovation, we provide every opportunity for the growth and development of our people, and we hope that you will also contribute to the growth of Rapid Innovation.</p>
                    <p>We look forward to a lasting relationship between us.</p>
                    <p>Best wishes for your new endeavors !!</p>
                    <p>Please feel free to contact us if you have any queries.</p>
                    <br>
                    <p>Best regards,<br>
                    Team HR<br>
                    Rapid Innovation</p>
                    </body>
                    </html>
                    """
                else:  # Contractor
                    subject = f'Rapid Innovation - Contractor\'s Agreement - {data["candidate_name"]}'
                    email_body = f"""
                    <html>
                    <body>
                    <p>Hello {data['candidate_name']},</p>
                    <p>Greetings from Rapid Innovation.</p>
                    <p>As discussed, we are pleased to extend the offer as a Contractor at Rapid Innovation, starting on or before {data['start_date'].strftime('%B %d, %Y')}.</p>
                    <p>PFA the copy of the agreement for your ready reference. Kindly revert with your acceptance by sending the duly signed copy of the letter. This opportunity is a permanent remote job.</p>
                    <p>At Rapid Innovation, we provide every possible opportunity for the growth and development of our people, and we hope that you will also contribute to its growth.</p>
                    <p>We look forward to a long-lasting relationship between us.</p>
                    <p>Best wishes for your new endeavors !!</p>
                    <p>Please don't hesitate to contact us if you have any questions.</p>
                    <br>
                    <p>Thanks & Regards<br>
                    Team HR<br>
                    Rapid Innovation</p>
                    </body>
                    </html>
                    """

                # Convert HTML to PDF
                pdf_bytes = convert_html_to_pdf(st.session_state.offer_letter_html)
                if pdf_bytes:
                    pdf_filename = f"{data['offer_type'].lower().replace(' ', '_')}_letter_{data['candidate_name'].replace(' ', '_')}.pdf"

                    # Send email with PDF attachment
                    success, message = send_email(
                        st.session_state.email_config['smtp_server'],
                        st.session_state.email_config['smtp_port'],
                        st.session_state.email_config['sender_email'],
                        st.session_state.email_config['sender_password'],
                        data['candidate_email'],
                        data['cc_list'],
                        subject,
                        email_body,
                        pdf_bytes,
                        pdf_filename
                    )

                    if success:
                        st.markdown('<div class="success-box">✅ Offer letter sent successfully!</div>',
                                  unsafe_allow_html=True)

                        # Show email preview
                        with st.expander("📧 Email Sent - Details"):
                            st.markdown(f"**To:** {data['candidate_email']}")
                            if data['cc_list']:
                                st.markdown(f"**CC:** {', '.join(data['cc_list'])}")
                            st.markdown(f"**Subject:** {subject}")
                            st.markdown("**Body:**")
                            st.markdown(email_body, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to generate PDF. Please check if wkhtmltopdf is installed.")

elif page == "📋 Phase 3: Appointment Letters":
    st.markdown("""
    <div class="section-header">
        <h2>📋 Phase 3: Appointment Letter Sending</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.email_config['configured']:
        st.warning("⚠️ Please configure email settings first in the Email Configuration section.")
        st.stop()

    st.info("Upload an appointment letter PDF and send it via email.")

    with st.form("appointment_email_form"):
        col1, col2 = st.columns(2)

        with col1:
            # PDF Upload
            uploaded_pdf = st.file_uploader("Upload Appointment Letter PDF*", type=['pdf'])
            recipient_email = st.text_input("Recipient Email*", placeholder="employee@example.com")

        with col2:
            subject = st.text_input("Email Subject*",
                                  value="Appointment Letter - Rapid Innovation",
                                  placeholder="Appointment Letter - Employee Name")
            cc_emails = st.text_area("CC Emails (one per line)",
                                    placeholder="hr@rapidinnovation.com\nmanager@rapidinnovation.com")

        email_body = st.text_area("Email Message*",
                                value="""Dear Employee,

Please find attached your appointment letter for your position at Rapid Innovation.

We are excited to have you join our team!

Best regards,
HR Team
Rapid Innovation""", height=150)

        send_email_btn = st.form_submit_button("📤 Send Appointment Letter")

        if send_email_btn:
            if uploaded_pdf and recipient_email and subject and email_body:
                if validate_email(recipient_email):
                    # Parse CC emails
                    cc_list = [email.strip() for email in cc_emails.split('\n') if email.strip() and validate_email(email.strip())]

                    # Read PDF file
                    pdf_bytes = uploaded_pdf.read()
                    pdf_filename = uploaded_pdf.name

                    # Convert plain text email body to HTML format
                    html_email_body = f"""
                    <html>
                    <body>
                    {email_body.replace(chr(10), '<br>')}
                    </body>
                    </html>
                    """

                    # Send email with PDF attachment
                    success, message = send_email(
                        st.session_state.email_config['smtp_server'],
                        st.session_state.email_config['smtp_port'],
                        st.session_state.email_config['sender_email'],
                        st.session_state.email_config['sender_password'],
                        recipient_email,
                        cc_list,
                        subject,
                        html_email_body,
                        pdf_bytes,
                        pdf_filename
                    )

                    if success:
                        st.markdown('<div class="success-box">✅ Appointment letter sent successfully!</div>',
                                  unsafe_allow_html=True)

                        # Show email preview
                        with st.expander("📧 Email Preview"):
                            st.markdown(f"**To:** {recipient_email}")
                            if cc_list:
                                st.markdown(f"**CC:** {', '.join(cc_list)}")
                            st.markdown(f"**Subject:** {subject}")
                            st.markdown(f"**Attachment:** {pdf_filename}")
                            st.markdown("**Body:**")
                            st.text(email_body)
                    else:
                        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                else:
                    st.error("Please enter a valid recipient email address.")
            else:
                st.error("Please fill in all required fields and upload a PDF file.")



elif page == "🎯 Phase 4: Welcome & Onboarding":
    st.markdown("""
    <div class="section-header">
        <h2>🎯 Phase 4: Welcome & System Enrollment</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.email_config['configured']:
        st.warning("⚠️ Please configure email settings first in the Email Configuration section.")
        st.stop()

    with st.form("welcome_email_form"):
        col1, col2 = st.columns(2)

        with col1:
            employee_name = st.text_input("Employee Name*", placeholder="John Doe")
            employee_official_email = st.text_input("Official Email*", placeholder="john.doe@rapidinnovation.com")

        with col2:
            cc_emails = st.text_area("CC Emails (one per line)", placeholder="hr@rapidinnovation.com")
            joining_form_url = st.text_input("Joining Form URL",
                                           value="https://docs.google.com/forms/d/1TVQyWZzwzIGxIB6opxZxk8GJOI_HoF15-4Oa7Q4zEjA/edit?ts=61fb8f9f")

        submitted = st.form_submit_button("🎯 Send Welcome Email")

        if submitted:
            if employee_name and employee_official_email:
                if validate_email(employee_official_email):
                    # Parse CC emails
                    cc_list = [email.strip() for email in cc_emails.split('\n') if email.strip() and validate_email(email.strip())]

                    # Generate email content
                    subject = f'Welcome On Board - {employee_name}'
                    email_body = f"""
                    <html>
                    <body>
                    <p>Dear {employee_name},</p>

                    <p>Greetings of the day !!</p>

                    <p>We are happy to have you join our organization. We believe that you will be a great asset to our company.</p>

                    <p>Again, Congratulations. We are thrilled to have you join the team and look forward to working with you.</p>

                    <p>As a part of the process, I have attached a form link to this mail kindly fill out that form:</p>

                    <p><a href="{joining_form_url}" target="_blank">{joining_form_url}</a></p>

                    <h3>System Enrollment Information:</h3>
                    <p>You will be enrolled in the following platforms:</p>
                    <ul>
                        <li><strong>Gmail/Email:</strong> Official company email ID (already created)</li>
                        <li><strong>Slack:</strong> Communication and collaboration platform</li>
                        <li><strong>TeamLogger:</strong> Time tracking and work management</li>
                        <li><strong>Razorpay:</strong> Payment and expense management (if applicable)</li>
                    </ul>

                    <p>Please let me know if you have any questions.</p>

                    <br>
                    <p>Regards<br>
                    Team HR<br>
                    Rapid Innovation</p>
                    </body>
                    </html>
                    """

                    # Send email
                    success, message = send_email(
                        st.session_state.email_config['smtp_server'],
                        st.session_state.email_config['smtp_port'],
                        st.session_state.email_config['sender_email'],
                        st.session_state.email_config['sender_password'],
                        employee_official_email,
                        cc_list,
                        subject,
                        email_body
                    )

                    if success:
                        st.markdown('<div class="success-box">✅ Welcome email sent successfully!</div>',
                                  unsafe_allow_html=True)

                        # Show preview
                        with st.expander("📧 Email Preview"):
                            st.markdown(f"**To:** {employee_official_email}")
                            if cc_list:
                                st.markdown(f"**CC:** {', '.join(cc_list)}")
                            st.markdown(f"**Subject:** {subject}")
                            st.markdown("**Body:**")
                            st.markdown(email_body, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                else:
                    st.error("Please enter a valid official email address.")
            else:
                st.error("Please fill in all required fields.")

elif page == "🔍 Phase 5: Background Verification":
    st.markdown("""
    <div class="section-header">
        <h2>🔍 Phase 5: Background Verification</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.email_config['configured']:
        st.warning("⚠️ Please configure email settings first in the Email Configuration section.")
        st.stop()

    st.info("This phase is for experienced full-time employees only.")

    with st.form("bgv_email_form"):
        col1, col2 = st.columns(2)

        with col1:
            employee_name = st.text_input("Employee Name*", placeholder="John Doe")
            previous_company_hr_email = st.text_input("Previous Company HR Email*", placeholder="hr@previouscompany.com")
            employee_id = st.text_input("Employee ID (if known)", placeholder="EMP001")
            designation = st.text_input("Previous Designation*", placeholder="Software Engineer")

        with col2:
            employment_period = st.text_input("Period of Employment*", placeholder="Jan 2020 - Dec 2022")
            reporting_manager = st.text_input("Reporting Manager", placeholder="Manager Name")
            cc_emails = st.text_area("CC Emails (one per line)", placeholder="hr@rapidinnovation.com")

        submitted = st.form_submit_button("🔍 Send BGV Email")

        if submitted:
            if employee_name and previous_company_hr_email and designation and employment_period:
                if validate_email(previous_company_hr_email):
                    # Parse CC emails
                    cc_list = [email.strip() for email in cc_emails.split('\n') if email.strip() and validate_email(email.strip())]

                    # Generate BGV email content
                    subject = f'Employee Background Verification - {employee_name} - Rapid Innovation'
                    email_body = f"""
                    <html>
                    <body>
                    <p>Dear HR,</p>

                    <p>I hope you are doing great !!</p>

                    <p>This is about the Background Verification of "{employee_name}" who worked in your esteemed organization.</p>

                    <p>Please find below, the form for Background verification. It would be very kind if you could spare a few minutes and verify the information provided by {employee_name}.</p>

                    <table border="1" cellpadding="10" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                        <tr style="background-color: #f2f2f2;">
                            <th>Particulars</th>
                            <th>Details provided by Candidate</th>
                            <th>Details as per company records</th>
                        </tr>
                        <tr>
                            <td><strong>Employee Name</strong></td>
                            <td>{employee_name}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Employee ID</strong></td>
                            <td>{employee_id if employee_id else 'Please specify'}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Designation</strong><br>(In case of a mismatch, please clarify with reason)</td>
                            <td>{designation}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Period of Employment</strong></td>
                            <td>{employment_period}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Reporting to</strong><br>(In case of a mismatch, please confirm if the employee ever reported to the stated supervisor-directly or indirectly)</td>
                            <td>{reporting_manager if reporting_manager else 'Please specify'}</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Character & Conduct</strong></td>
                            <td>Please specify</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Reason for Leaving</strong></td>
                            <td>Please specify</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Eligible for rehire</strong><br>(If No, kindly specify the reason)</td>
                            <td>Please specify</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Status of Exit Formalities</strong><br>(In case of pending; please specify from whose side- candidate or company)</td>
                            <td>Please specify</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Are the Attached Documents Genuine?</strong><br>(If No, kindly Specify the reason – for e.g. is the document forged or fake or manipulated or any other reason)</td>
                            <td>Attached</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Additional Comments</strong></td>
                            <td>Please specify</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><strong>Name and Job title of the verifying Authority</strong></td>
                            <td>Please specify</td>
                            <td></td>
                        </tr>
                    </table>

                    <p>Feel free to get in touch if you have any questions.</p>

                    <br>
                    <p>Regards<br>
                    Team HR<br>
                    Rapid Innovation</p>
                    </body>
                    </html>
                    """

                    # Send email
                    success, message = send_email(
                        st.session_state.email_config['smtp_server'],
                        st.session_state.email_config['smtp_port'],
                        st.session_state.email_config['sender_email'],
                        st.session_state.email_config['sender_password'],
                        previous_company_hr_email,
                        cc_list,
                        subject,
                        email_body
                    )

                    if success:
                        st.markdown('<div class="success-box">✅ Background verification email sent successfully!</div>',
                                  unsafe_allow_html=True)

                        # Show preview
                        with st.expander("📧 Email Preview"):
                            st.markdown(f"**To:** {previous_company_hr_email}")
                            if cc_list:
                                st.markdown(f"**CC:** {', '.join(cc_list)}")
                            st.markdown(f"**Subject:** {subject}")
                            st.markdown("**Body:**")
                            st.markdown(email_body, unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)
                else:
                    st.error("Please enter a valid HR email address.")
            else:
                st.error("Please fill in all required fields.")

elif page == "🚪 Phase 6: Exit Process":
    st.markdown("""
    <div class="section-header">
        <h2>🚪 Phase 6: Exit Process Management</h2>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.email_config['configured']:
        st.warning("⚠️ Please configure email settings first in the Email Configuration section.")
        st.stop()

    # Initialize session state for exit process
    if 'exit_process_data' not in st.session_state:
        st.session_state.exit_process_data = {}

    # Exit process tabs
    tab1, tab2, tab3 = st.tabs(["📋 Phase 1: Initiation", "📦 Phase 2: Assets & Access", "📜 Phase 3: Certificates"])

    with tab1:
        st.markdown("### 📋 Phase 1: Exit Initiation & Communication")

        # Manager Confirmation Email
        with st.expander("📧 Manager Confirmation Email", expanded=True):
            with st.form("manager_confirmation_form"):
                col1, col2 = st.columns(2)

                with col1:
                    employee_name = st.text_input("Employee Name*", placeholder="John Doe")
                    manager_name = st.text_input("Manager Name*", placeholder="Jane Smith")
                    manager_email = st.text_input("Manager Email*", placeholder="jane@rapidinnovation.com")

                with col2:
                    last_working_day = st.date_input("Last Working Day*")
                    cc_emails = st.text_area("CC Emails (one per line)", placeholder="hr@rapidinnovation.com")

                if st.form_submit_button("📧 Send Manager Confirmation"):
                    if employee_name and manager_name and manager_email and last_working_day:
                        if validate_email(manager_email):
                            cc_list = [email.strip() for email in cc_emails.split('\n') if email.strip() and validate_email(email.strip())]

                            subject = f'Confirmation for proceeding with the Exit formalities - {employee_name}'
                            email_body = f"""
                            <html>
                            <body>
                            <p>Hi {manager_name},</p>
                            <p>I hope you are doing well !!</p>
                            <p>As you know, <strong>{last_working_day.strftime('%d %B %Y')}</strong> is the last working day of <strong>{employee_name}</strong>.</p>
                            <p>Kindly let me know once all his knowledge transfer is done so that I can proceed with his exit formalities. These formalities include deactivating his official email ID (once deactivated cannot be restored) and removing him from Slack. Kindly let us know if the official mail data has to be transferred to any other account.</p>
                            <p>Also please take care of any software he is using like the GitHub account, also please remove him from project groups.</p>
                            <p>Please let me know in case of any queries.</p>
                            <br>
                            <p>Regards,<br>
                            Team HR<br>
                            Rapid Innovation</p>
                            </body>
                            </html>
                            """

                            success, message = send_email(
                                st.session_state.email_config['smtp_server'],
                                st.session_state.email_config['smtp_port'],
                                st.session_state.email_config['sender_email'],
                                st.session_state.email_config['sender_password'],
                                manager_email,
                                cc_list,
                                subject,
                                email_body
                            )

                            if success:
                                st.success("✅ Manager confirmation email sent successfully!")
                            else:
                                st.error(f"❌ Failed to send email: {message}")
                        else:
                            st.error("Please enter a valid manager email address.")
                    else:
                        st.error("Please fill in all required fields.")

        # Employee Exit Email
        with st.expander("📧 Employee Exit Notification"):
            with st.form("employee_exit_form"):
                col1, col2 = st.columns(2)

                with col1:
                    emp_name = st.text_input("Employee Name*", placeholder="John Doe", key="exit_emp_name")
                    emp_email = st.text_input("Employee Email*", placeholder="john@rapidinnovation.com")
                    emp_type = st.selectbox("Employee Type*", ["Intern", "Full-time Employee"])

                with col2:
                    lwd = st.date_input("Last Working Day*", key="exit_lwd")
                    manager_email_transfer = st.text_input("Manager Email (for file transfer)", placeholder="manager@rapidinnovation.com")
                    cc_emails_exit = st.text_area("CC Emails (one per line)", placeholder="hr@rapidinnovation.com", key="exit_cc")

                if st.form_submit_button("📧 Send Exit Notification"):
                    if emp_name and emp_email and emp_type and lwd:
                        if validate_email(emp_email):
                            cc_list = [email.strip() for email in cc_emails_exit.split('\n') if email.strip() and validate_email(email.strip())]

                            subject = f'Exit Formalities - {emp_name} - {lwd.strftime("%d %B %Y")}'

                            if emp_type == "Intern":
                                email_body = f"""
                                <html>
                                <body>
                                <p>Hi {emp_name},</p>
                                <p>This is to confirm that your last working day at Rapid Innovation is <strong>{lwd.strftime('%A, %d %B %Y')}</strong>.</p>
                                <p>You are requested to please look into the following points:</p>
                                <ol>
                                    <li>Please change all the communication addresses, if any are provided as the company's address.</li>
                                    <li>Your invoices will be considered as payslips.</li>
                                    <li>Please refer to the following Link to the exit feedback form and submit your valuable feedback on or before your last working day.</li>
                                    <li>Also, refer to the internship Letter signed by you at the time of Joining Rapid Innovation so that you can adhere to all the clauses mentioned in it.</li>
                                    <li>Kindly move all the files to a folder in the drive and provide ownership to {manager_email_transfer if manager_email_transfer else "your manager's email ID"}</li>
                                </ol>
                                <p>Your full and final settlement will be processed within 30-45 days from your last working day. HR will be sending the FNF statement to your email ID.</p>
                                <br>
                                <p>Regards<br>
                                Team HR</p>
                                </body>
                                </html>
                                """
                            else:
                                email_body = f"""
                                <html>
                                <body>
                                <p>Hi {emp_name},</p>
                                <p>This is to confirm that your last working day at Rapid Innovation is <strong>{lwd.strftime('%A, %d %B %Y')}</strong>.</p>
                                <p>You are requested to please look into the following points:</p>
                                <ol>
                                    <li>Please change all the communication addresses, if any are provided as the company's address.</li>
                                    <li>All your payslips are available on Razorpay; we expect you to download them and take them with you.</li>
                                    <li>Please ensure to submit all company belongings to the people concerned on the last working day, like a laptop, bag, mouse, headphones, and dongle (if any).</li>
                                    <li>If you wish to withdraw your PF amount, you can do that on the online PF portal. (People having less than 6 months of experience with us will not be eligible to withdraw the PF amount)</li>
                                    <li>Please refer to the following Link to the exit feedback form and submit your valuable feedback on or before your last working day.</li>
                                    <li>Also, refer to the Appointment Letter signed by you at the time of Joining Rapid Innovation so that you can adhere to all the clauses mentioned in it.</li>
                                    <li>Kindly move all the files to a folder in the drive and provide ownership to {manager_email_transfer if manager_email_transfer else "your manager's email ID"}</li>
                                </ol>
                                <p>Your full and final settlement will be processed within 30-45 days from your last working day. HR will be sending the FNF statement to your email ID.</p>
                                <br>
                                <p>Regards<br>
                                Team HR<br>
                                Rapid Innovation</p>
                                </body>
                                </html>
                                """

                            success, message = send_email(
                                st.session_state.email_config['smtp_server'],
                                st.session_state.email_config['smtp_port'],
                                st.session_state.email_config['sender_email'],
                                st.session_state.email_config['sender_password'],
                                emp_email,
                                cc_list,
                                subject,
                                email_body
                            )

                            if success:
                                st.success("✅ Exit notification email sent successfully!")
                            else:
                                st.error(f"❌ Failed to send email: {message}")
                        else:
                            st.error("Please enter a valid employee email address.")
                    else:
                        st.error("Please fill in all required fields.")

    with tab2:
        st.markdown("### 📦 Phase 2: Asset & Access Management")

        # Asset Return Email
        with st.expander("📦 Asset Return Email", expanded=True):
            with st.form("asset_return_form"):
                col1, col2 = st.columns(2)

                with col1:
                    asset_emp_name = st.text_input("Employee Name*", placeholder="John Doe", key="asset_emp_name")
                    asset_emp_email = st.text_input("Employee Email*", placeholder="john@rapidinnovation.com", key="asset_emp_email")
                    asset_emp_personal_email = st.text_input("Personal Email*", placeholder="john.personal@gmail.com")

                with col2:
                    asset_type = st.selectbox("Asset Type*", ["Macbook", "Windows Laptop", "Other"])
                    return_address = st.text_area("Return Address*", value="Hotel North 39, Junas Wada, near River Bridge, Mandrem, Goa 403524")
                    contact_person = st.text_input("Contact Person", value="Armond Fernandes")
                    contact_number = st.text_input("Contact Number", value="9823268663")

                if st.form_submit_button("📦 Send Asset Return Email"):
                    if asset_emp_name and asset_emp_email and asset_emp_personal_email and asset_type:
                        if validate_email(asset_emp_email) and validate_email(asset_emp_personal_email):
                            subject = "Asset Dispatch Details"
                            email_body = f"""
                            <html>
                            <body>
                            <p>Hello {asset_emp_name},</p>
                            <p>We hope you are doing well !!</p>
                            <p>You are requested to return the company-owned <strong>{asset_type}</strong>.</p>
                            <p><strong>Details of the Dispatch:</strong></p>
                            <ul>
                                <li><strong>Name:</strong> {contact_person}</li>
                                <li><strong>Address:</strong> {return_address}</li>
                                <li><strong>Contact Number:</strong> {contact_number}</li>
                            </ul>
                            <p><strong>Please note:</strong></p>
                            <ol>
                                <li>We will proceed with your FNF settlement once we will receive the company's assets in good condition.</li>
                                <li>Kindly attach a photo or video of the device before dispatching it to the address above. {"Please take insurance in case of Macbook." if asset_type == "Macbook" else ""}</li>
                            </ol>
                            <p>Please reach out to us in case of any queries.</p>
                            <br>
                            <p>Thanks & Regards<br>
                            Team HR<br>
                            Rapid Innovation</p>
                            </body>
                            </html>
                            """

                            success, message = send_email(
                                st.session_state.email_config['smtp_server'],
                                st.session_state.email_config['smtp_port'],
                                st.session_state.email_config['sender_email'],
                                st.session_state.email_config['sender_password'],
                                asset_emp_email,
                                [asset_emp_personal_email],  # CC to personal email
                                subject,
                                email_body
                            )

                            if success:
                                st.success("✅ Asset return email sent successfully!")
                            else:
                                st.error(f"❌ Failed to send email: {message}")
                        else:
                            st.error("Please enter valid email addresses.")
                    else:
                        st.error("Please fill in all required fields.")

        # Access Removal Checklist
        with st.expander("🔐 Access Removal Checklist"):
            st.markdown("### 🔐 Remove All Credentials from All Platforms")
            st.markdown("**Checklist for IT Department:**")

            platforms = [
                "Company Email",
                "Slack",
                "TeamLogger",
                "Project Management Tools",
                "Internal Drives/Servers",
                "GitHub/GitLab",
                "Software Licenses",
                "VPN Access",
                "Other Platforms"
            ]

            st.markdown("**Employee:** " + st.text_input("Employee Name for Access Removal", key="access_removal_name"))

            for platform in platforms:
                st.checkbox(f"✅ {platform}", key=f"access_{platform.lower().replace(' ', '_').replace('/', '_')}")

            if st.button("📋 Generate Access Removal Report"):
                checked_platforms = []
                for platform in platforms:
                    key = f"access_{platform.lower().replace(' ', '_').replace('/', '_')}"
                    if st.session_state.get(key, False):
                        checked_platforms.append(platform)

                if checked_platforms:
                    st.success(f"✅ Access removed from: {', '.join(checked_platforms)}")
                else:
                    st.warning("⚠️ No platforms selected for access removal.")

    with tab3:
        st.markdown("### 📜 Phase 3: Final Settlement & Documentation")

        # Experience Letter/Certificate Generation
        with st.expander("📜 Generate Experience Letter/Certificate", expanded=True):
            with st.form("certificate_form"):
                col1, col2 = st.columns(2)

                with col1:
                    cert_title = st.selectbox("Title*", ["Mr.", "Ms."], key="cert_title")
                    cert_emp_name = st.text_input("Employee Name*", placeholder="John Doe", key="cert_emp_name")
                    cert_emp_email = st.text_input("Personal Email*", placeholder="john.personal@gmail.com", key="cert_emp_email")
                    cert_position = st.text_input("Position*", placeholder="Software Engineer", key="cert_position")

                with col2:
                    # Set default dates - 1 year ago to today
                    default_start = datetime.now() - timedelta(days=365)
                    default_end = datetime.now()

                    cert_start_date = st.date_input(
                        "Employment Start Date*",
                        value=default_start.date(),
                        help="Select the date when the employee started working",
                        key="cert_start_date"
                    )
                    cert_end_date = st.date_input(
                        "Employment End Date*",
                        value=default_end.date(),
                        help="Select the date when the employee's employment ended",
                        key="cert_end_date"
                    )
                    cert_type = st.selectbox("Certificate Type*", [
                        "Standard Experience Letter",
                        "Internship Certificate",
                        "Experience Letter (Dues Not Settled)"
                    ])

                if st.form_submit_button("📜 Generate Certificate"):
                    if cert_title and cert_emp_name and cert_emp_email and cert_position and cert_start_date and cert_end_date:
                        if cert_end_date <= cert_start_date:
                            st.error("❌ End date must be after start date!")
                        elif validate_email(cert_emp_email):
                            # Determine letter type
                            if cert_type == "Internship Certificate":
                                letter_type = "internship"
                                subject = f"Rapid Innovation - Internship Certificate - {cert_emp_name}"
                                email_intro = "PFA: Internship Certificate"
                            elif cert_type == "Experience Letter (Dues Not Settled)":
                                letter_type = "dues_not_settled"
                                subject = f"Rapid Innovation - Experience Letter - {cert_emp_name}"
                                email_intro = "PFA, your Experience Letter."
                            else:
                                letter_type = "standard"
                                subject = f"Rapid Innovation - Experience Letter - {cert_emp_name}"
                                email_intro = "PFA, your Experience Letter."

                            # Generate certificate HTML
                            certificate_html = generate_experience_letter(
                                f"{cert_title} {cert_emp_name}",
                                cert_position,
                                cert_start_date,
                                cert_end_date,
                                letter_type
                            )

                            # Store in session state for preview
                            st.session_state.certificate_html = certificate_html
                            st.session_state.certificate_data = {
                                'name': cert_emp_name,
                                'email': cert_emp_email,
                                'position': cert_position,
                                'start_date': cert_start_date,
                                'end_date': cert_end_date,
                                'type': cert_type,
                                'subject': subject,
                                'email_intro': email_intro
                            }

                            st.success("✅ Certificate generated successfully! See preview below.")
                        else:
                            st.error("Please enter a valid email address.")
                    else:
                        st.error("Please fill in all required fields.")

        # Certificate Preview and Send
        if 'certificate_html' in st.session_state and 'certificate_data' in st.session_state:
            st.markdown("---")

            # Preview
            with st.expander("📋 Certificate Preview", expanded=True):
                st.markdown(st.session_state.certificate_html, unsafe_allow_html=True)

            # Download and Send Options
            st.markdown("### 📥 Download & Send Options")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📄 Download as PDF", key="cert_download"):
                    pdf_bytes = convert_html_to_pdf(st.session_state.certificate_html)
                    if pdf_bytes:
                        # Simplify filename based on certificate type
                        data = st.session_state.certificate_data
                        if "internship" in data['type'].lower():
                            filename = "internship_certificate.pdf"
                        elif "dues not settled" in data['type'].lower():
                            filename = "experience_letter_dues_not_settled.pdf"
                        else:
                            filename = "experience_letter.pdf"

                        st.download_button(
                            label="💾 Download PDF",
                            data=pdf_bytes,
                            file_name=filename,
                            mime="application/pdf"
                        )
                    else:
                        st.error("❌ Failed to generate PDF.")

            with col2:
                if st.button("📧 Send Email with PDF", key="cert_send"):
                    data = st.session_state.certificate_data

                    email_body = f"""
                    <html>
                    <body>
                    <p>Hi {data['name']},</p>
                    <p>I hope you are doing well.</p>
                    <p>{data['email_intro']}</p>
                    <p>Kindly reach out to us if you have any concerns.</p>
                    <br>
                    <p>Thanks & Regards<br>
                    Team HR<br>
                    Rapid Innovation</p>
                    </body>
                    </html>
                    """

                    # Convert HTML to PDF
                    pdf_bytes = convert_html_to_pdf(st.session_state.certificate_html)
                    if pdf_bytes:
                        # Simplify filename based on certificate type
                        if "internship" in data['type'].lower():
                            pdf_filename = "internship_certificate.pdf"
                        elif "dues not settled" in data['type'].lower():
                            pdf_filename = "experience_letter_dues_not_settled.pdf"
                        else:
                            pdf_filename = "experience_letter.pdf"

                        # Send email with PDF attachment
                        success, message = send_email(
                            st.session_state.email_config['smtp_server'],
                            st.session_state.email_config['smtp_port'],
                            st.session_state.email_config['sender_email'],
                            st.session_state.email_config['sender_password'],
                            data['email'],
                            [],  # No CC for certificates
                            data['subject'],
                            email_body,
                            pdf_bytes,
                            pdf_filename
                        )

                        if success:
                            st.success("✅ Certificate sent successfully!")
                        else:
                            st.error(f"❌ Failed to send email: {message}")
                    else:
                        st.error("❌ Failed to generate PDF.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🚀 <strong>Rapid Innovation Onboarding Automation System</strong></p>
    <p>Streamlining your HR processes with automation and efficiency</p>
</div>
""", unsafe_allow_html=True)
