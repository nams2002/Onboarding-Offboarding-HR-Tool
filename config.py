# Configuration file for Rapid Innovation Onboarding Automation System

# Company Information
COMPANY_NAME = "Rapid Innovation"
COMPANY_FULL_NAME = "Rapid Innovation Pvt. Ltd."
HR_TEAM_NAME = "Team HR"

# Default Email Settings
DEFAULT_CC_EMAIL = "hr@rapidinnovation.com"
DEFAULT_JOINING_FORM_URL = "https://docs.google.com/forms/d/1TVQyWZzwzIGxIB6opxZxk8GJOI_HoF15-4Oa7Q4zEjA/edit?ts=61fb8f9f"

# Image Paths
HEADER_IMAGE_PATH = "images/Rapid Innovation Header (1).png"
FOOTER_IMAGE_PATH = "images/footer (1) copy (1) copy.png"
SIGNATURE_IMAGE_PATH = "images/Aarushi.sign.png"

# HR Manager Information
HR_MANAGER_NAME = "Aarushi Sharma"
HR_MANAGER_TITLE = "Assistant Manager HR"

# Default Terms and Conditions
DEFAULT_PROBATION_PERIOD = "3 months"
DEFAULT_NOTICE_PERIOD_CONFIRMED = "30 days"
DEFAULT_NOTICE_PERIOD_PROBATION = "15 days"
DEFAULT_MEDICAL_COVERAGE = "Group medical insurance scheme covers you and your family (Spouse & 02 Children). Maximum members allowed for coverage is 4."

# Platform Information for System Enrollment
PLATFORMS = {
    "Gmail": "Official company email ID",
    "Slack": "Communication and collaboration platform",
    "TeamLogger": "Time tracking and work management",
    "Razorpay": "Payment and expense management"
}

# Email Templates Customization
EMAIL_SIGNATURE = f"""
<br>
<p>Thanks & Regards<br>
{HR_TEAM_NAME}<br>
{COMPANY_NAME}</p>
"""

# Document Styling
DOCUMENT_STYLES = {
    "primary_color": "#1e3c72",
    "secondary_color": "#2a5298",
    "font_family": "Arial, sans-serif",
    "line_height": "1.6"
}
