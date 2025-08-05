# 🚀 Rapid Innovation - Onboarding Automation System

A comprehensive Streamlit-based web application that automates the complete employee onboarding process for Rapid Innovation. This system streamlines document generation, email communication, and workflow management for HR teams.

## ✨ Features

### 📧 **Email Integration**
- SMTP configuration for direct email sending
- Email validation and verification
- Automatic CC/BCC support
- Attachment handling for documents

### 📝 **Phase 1: Initial Document Requests**
- Automated email templates for interns and full-time employees
- Customizable document requirement lists
- Professional email formatting

### 📄 **Phase 2: Offer Letter Generation**
- Professional offer letters for:
  - Interns
  - Full-time Employees
  - Contractors
- Company branding with headers and footers
- PDF generation and email attachment

### 📋 **Phase 3: Appointment Letters**
- Comprehensive appointment letters with terms & conditions
- Legal agreements and NDAs
- Digital signature integration
- Professional formatting with company branding

### 🎯 **Phase 4: Welcome & System Enrollment**
- Welcome emails with joining forms
- Platform enrollment information (Gmail, Slack, TeamLogger, Razorpay)
- Onboarding checklist and instructions

### 🔍 **Phase 5: Background Verification**
- Automated BGV emails to previous employers
- Structured verification forms
- Professional communication templates

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd onboarding-automation
```

### Step 2: Quick Installation (Recommended)
```bash
python install.py
```

### Step 3: Manual Installation (Alternative)
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
1. Copy `.env.template` to `.env` (if not already done)
2. Update `.env` with your email credentials:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=hrms@rapidinnovation.dev
SMTP_PASSWORD=your_app_password
DEFAULT_SENDER_EMAIL=hrms@rapidinnovation.dev
DEFAULT_SENDER_NAME=Rapid Innovation HR
```

### Step 5: Setup Images
Ensure the following images are placed in the `images/` folder:
- `Rapid Innovation Header (1).png` - Company header
- `footer (1) copy (1) copy.png` - Company footer
- `Aarushi.sign.png` - HR signature image

### Step 6: Run the Application
```bash
# Easy method (Windows)
run.bat

# Python method
python run.py

# Direct method
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📧 Email Configuration

### Gmail Setup (Recommended)
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Use these settings in the app:
   - **SMTP Server:** `smtp.gmail.com`
   - **SMTP Port:** `587`
   - **Email:** Your Gmail address
   - **Password:** The generated app password

### Other Email Providers
- **Outlook:** `smtp-mail.outlook.com:587`
- **Yahoo:** `smtp.mail.yahoo.com:587`
- **Custom SMTP:** Contact your email provider for settings

## 🎯 Usage Guide

### 1. Initial Setup
1. Navigate to "📧 Email Configuration"
2. Enter your SMTP settings
3. Test the configuration with a test email

### 2. Document Generation Workflow
1. **Phase 1:** Send initial document requests to new hires
2. **Phase 2:** Generate and send offer letters
3. **Phase 3:** Create appointment letters with legal terms
4. **Phase 4:** Send welcome emails and enrollment information
5. **Phase 5:** Initiate background verification (for experienced hires)

### 3. Email Features
- All emails include professional formatting
- Automatic CC to HR team
- Email validation before sending
- Preview functionality before sending
- Attachment support for generated documents

## 🔧 Customization

### Email Templates
Email templates can be customized by modifying the HTML content in the respective phase functions within `app.py`.

### Document Templates
- Offer letter templates: Modify `generate_offer_letter()` function
- Appointment letter templates: Modify `generate_appointment_letter()` function

### Company Branding
Replace images in the `images/` folder with your company's branding materials.

## 🚨 Troubleshooting

### Email Issues
- **Authentication Error:** Check email credentials and app password
- **SMTP Error:** Verify SMTP server and port settings
- **Attachment Error:** Ensure images exist in the `images/` folder

### Application Issues
- **Import Error:** Run `pip install -r requirements.txt`
- **Image Not Found:** Check image paths in the `images/` folder
- **Streamlit Error:** Update Streamlit: `pip install --upgrade streamlit`

## 📁 Project Structure
```
onboarding-automation/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── images/               # Company branding images
│   ├── Rapid Innovation Header (1).png
│   ├── footer (1) copy (1) copy.png
│   └── Aarushi.sign.png
└── aim.txt              # Original requirements document
```

## 🔒 Security Notes

- Never commit email passwords to version control
- Use app passwords instead of main account passwords
- Consider using environment variables for sensitive data
- Regularly update dependencies for security patches

## 🤝 Support

For technical support or feature requests, please contact the development team.

## 📄 License

This project is proprietary software developed for Rapid Innovation.

---

**Built with ❤️ using Streamlit for Rapid Innovation**
