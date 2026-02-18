
import streamlit as st
from fpdf import FPDF
import io
from data_ingestion.airtable_data import load_all_airtable
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity
from genai.summary import generate_summary


# --- PDF Class Definition ---
class PDF(FPDF):
    def header(self):
        self.set_fill_color(15, 32, 39)
        self.rect(0, 0, 210, 30, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 18)
        self.cell(0, 18, 'Executive Summary', ln=True, align='C')
        self.ln(2)

    def section_title(self, title):
        self.set_font('Arial', 'B', 13)
        self.set_text_color(29, 233, 182)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 60, 67)

    def section_body(self, text):
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 60, 67)
        self.multi_cell(0, 8, text)

    def bullet_list(self, items):
        self.set_font('Arial', '', 12)
        self.set_text_color(0, 60, 67)
        for item in items:
            self.cell(5)
            self.cell(0, 8, f"- {item}", ln=True)


def load_all_data():
    data = load_all_airtable()
    campaigns = data["campaigns"]
    accounts = data["accounts"]
    contacts = data["contacts"]
    attendees = data["attendees"]
    responses = data["responses"]
    activities = data["activities"]
    opportunities = data["opportunities"]
    return campaigns, accounts, contacts, attendees, responses, activities, opportunities


st.set_page_config(
    page_title="AI Powered Marketing Intelligence", layout="wide", page_icon="🧠")

# --- Custom CSS for modern look ---
st.markdown("""
<style>
.main {background: #f7fafc;}
.stButton>button {background: linear-gradient(90deg, #1de9b6, #2c5364); color: #fff; border-radius: 2rem; font-weight: 700; font-size: 1.1rem; padding: 0.6rem 2.2rem; border: none;}
.stButton>button:hover {background: linear-gradient(90deg, #2c5364, #1de9b6); color: #fff;}
.stTextArea textarea {border-radius: 1rem; border: 1.5px solid #1de9b6; font-size: 1.08rem;}
.stSelectbox>div>div {border-radius: 1rem;}
.summary-card {background: #fff; border-radius: 1.2rem; box-shadow: 0 2px 16px rgba(44,83,100,0.10); padding: 2.5rem 2.5rem 2rem 2.5rem; margin-top: 1.5rem;}
.summary-title {font-size: 2.1rem; font-weight: 800; color: #003c43; margin-bottom: 0.5rem;}
.summary-section {font-size: 1.18rem; font-weight: 600; color: #2c5364; margin-top: 1.2rem;}
.summary-badge {background: #1de9b6; color: #003c43; border-radius: 1rem; padding: 0.3rem 1.2rem; font-size: 1rem; font-weight: 700; margin-left: 1rem;}
.summary-key {font-weight: 700; color: #003c43;}
.summary-value {color: #2c5364; font-weight: 600;}
.download-btn {background: #1de9b6; color: #003c43; font-weight: 700; border: none; border-radius: 2rem; padding: 0.5rem 1.5rem; font-size: 1.1rem; margin-right: 1rem; text-decoration: none; display: inline-block;}
.download-btn:hover {background: #2c5364; color: #fff;}
.footer {margin-top: 2.5rem; color: #888; font-size: 1.02rem; text-align: center;}
</style>
""", unsafe_allow_html=True)

# --- Page Heading ---


# --- Sidebar for campaign selection ---
with st.sidebar:
    # App header moved to main page
    # --- Horizontal App Header ---
    st.markdown("""
    <div style='width: 100%; background: #f7fafc; border-bottom: 2px solid #1de9b6; padding: 1.1rem 0 0.7rem 0; margin-bottom: 1.2rem;'>
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center;'>
            <span style='font-size:2.1rem; font-weight:900; color:#003c43;'>🧠 AI Powered Marketing Intelligence</span>
            <span style='font-size:1.13rem; color:#2c5364; margin-top:0.18rem;'>Transforming campaign data into board-ready insights</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='font-size:1.2rem; font-weight:700; color:#003c43;'>Select Campaign</div>",
                unsafe_allow_html=True)
    try:
        campaigns, accounts, contacts, attendees, responses, activities, opportunities = load_all_data()
    except EnvironmentError as e:
        st.error(f"Airtable environment error: {e}")
        st.markdown("""
        **Environment Setup:**
        - Set your Airtable token and base ID securely as environment variables:
            - In your terminal or ~/.zshrc:
              ```
              export AIRTABLE_TOKEN="your_personal_access_token"
              export AIRTABLE_BASE_ID="your_base_id"
              ```
        - Never hardcode tokens in code or share them publicly.
        - Restart your terminal or run `source ~/.zshrc` before launching Streamlit.
        """)
        st.stop()
    except Exception as e:
        st.error(f"Airtable loading error: {e}")
        st.stop()
    campaign_options = {c.name: c for c in campaigns}
    if not campaign_options:
        st.warning("No campaigns found in Airtable. Please check your data.")
        st.stop()
    selected_campaign_name = st.selectbox(
        "Choose a Campaign", list(campaign_options.keys()), key="sidebar_campaign_select")
    selected_campaign = campaign_options[selected_campaign_name]


# --- Main Layout: Horizontal Split ---
selected_attendees = [
    a for a in attendees if a.campaign_id == selected_campaign.id]
selected_responses = [
    r for r in responses if r.campaign_id == selected_campaign.id]
selected_activities = [
    a for a in activities if a.campaign_id == selected_campaign.id]
selected_opportunities = [
    o for o in opportunities if o.campaign_id == selected_campaign.id]

left_col, right_col = st.columns([1, 2], gap="large")


def build_default_prompt(attendees, opportunities):
    num_attendees = len(attendees)
    pipeline = sum(o.amount for o in opportunities)
    num_opps = len(opportunities)
    prompt = f'''Please provide a bulleted executive summary for this campaign, including:

Format the summary as clear bullet points with real numbers and, if possible, use actual attendee names from the data in the output.
'''
    return prompt


default_prompt = build_default_prompt(
    selected_attendees, selected_opportunities)
with left_col:
    st.markdown("<div style='font-size:1.1rem; font-weight:600; color:#2c5364; margin-bottom:0.3rem;'>Customize Executive Summary Prompt</div>", unsafe_allow_html=True)
    user_prompt = st.text_area(
        "Customize Executive Summary Prompt",
        value=default_prompt,
        height=180,
        key="main_prompt_input",
        label_visibility="visible"
    )
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    generate = st.button("🚀 Generate Executive Summary",
                         key="main_generate_button",
                         help="Generate a new executive summary based on the selected campaign and prompt.",
                         use_container_width=False,
                         type="secondary"
                         )
    st.markdown("""
    <style>
    .stButton>button#main_generate_button {
        font-size: 1.02rem !important;
        padding: 0.35rem 1.2rem !important;
        border-radius: 1.2rem !important;
        background: linear-gradient(90deg, #1de9b6, #2c5364);
        color: #fff;
        font-weight: 700;
        border: none;
        margin-bottom: 0.2rem;
    }
    .stButton>button#main_generate_button:hover {
        background: linear-gradient(90deg, #2c5364, #1de9b6);
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
    if 'summary' not in st.session_state:
        st.session_state['summary'] = ''
    if generate:
        with st.spinner("Generating summary with GenAI..."):
            summary = generate_summary(
                campaigns=[selected_campaign],
                attendees=selected_attendees,
                responses=selected_responses,
                activities=selected_activities,
                contacts=contacts,
                accounts=accounts,
                opportunities=selected_opportunities,
                program_name=selected_campaign.name,
                user_prompt=user_prompt
            )
            st.session_state['summary'] = summary
        st.success("Executive summary generated!")
    st.session_state['selected_campaign'] = selected_campaign


with right_col:
    # --- Summary Card Rendering ---
    if st.session_state.get('summary') and st.session_state.get('selected_campaign'):
        campaign_name = st.session_state['selected_campaign'].name
        attendees_count = len(
            [a for a in attendees if a.campaign_id == st.session_state['selected_campaign'].id])
        pipeline_value = sum(getattr(o, 'amount', 0)
                             for o in opportunities if o.campaign_id == st.session_state['selected_campaign'].id)
        pipeline_display = f"${pipeline_value/1e6:.1f}M" if pipeline_value else "$0.0M"
        key_account_ids = set(
            [o.account_id for o in opportunities if o.campaign_id == st.session_state['selected_campaign'].id])
        key_accounts = [a.name for a in accounts if a.id in key_account_ids]
        accounts_display = " ".join([
            f"<span class='summary-badge'>{a}</span>" for a in key_accounts[:4]
        ]) if key_accounts else "N/A"
        impact_lines = [line.lstrip('-').strip() for line in st.session_state['summary'].split(
            '\n') if line.strip() and not line.strip().startswith('Campaign:')]
        impact_html = "".join([f"<li>{line}</li>" for line in impact_lines])
        st.markdown(f"""
<div class='summary-card' style='margin-top:2.2rem;'>
    <div style='display: flex; align-items: center; justify-content: space-between;'>
        <span class='summary-title'>Executive Summary</span>
        <span class='summary-badge'>Generated</span>
    </div>
    <hr style='border: 1.5px solid #1de9b6; margin: 0.5rem 0 1.2rem 0;'>
    <div style='font-size: 1.18rem; margin-bottom: 0.7rem;'><span class='summary-key'>Campaign:</span> <span class='summary-value'>{campaign_name}</span></div>
    <div style='display: flex; gap: 2.5rem; margin-bottom: 0.7rem;'>
        <div>👥 <span class='summary-key'>Attendees:</span> <span class='summary-value' style='font-size:1.5rem;'>{attendees_count}</span></div>
        <div>💰 <span class='summary-key'>Pipeline:</span> <span class='summary-value' style='font-size:1.5rem;'>{pipeline_display}</span></div>
    </div>
    <hr style='border: 1px solid #e0e0e0; margin: 0.7rem 0;'>
    <div style='margin-bottom: 0.7rem;'><span class='summary-key'>Key Accounts:</span> {accounts_display}</div>
    <hr style='border: 1px solid #e0e0e0; margin: 0.7rem 0;'>
    <div class='summary-section'>Strategic Impact</div>
    <ul style='margin: 0 0 0 1.2rem; padding: 0; color: #2c5364;'>
        {impact_html}
    </ul>
</div>
        """, unsafe_allow_html=True)
        # --- Download Buttons ---
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.section_title(f"Campaign: {campaign_name}")
        pdf.section_body(
            f"{attendees_count} Executives Attended    {pipeline_display} Pipeline Influence")
        pdf.section_title("Key Accounts:")
        import re
        accounts_clean = re.sub(r"<span[^>]*>", "", accounts_display)
        accounts_clean = accounts_clean.replace("</span>", ", ").strip(', ')
        pdf.section_body(accounts_clean)
        pdf.section_title("Strategic Impact")
        pdf.bullet_list([line for line in impact_lines])
        pdf_bytes = pdf.output(dest='S').encode('latin1', errors='replace')
        pdf_output = io.BytesIO(pdf_bytes)
        import base64
        summary_text = st.session_state['summary']
        summary_text_b64 = base64.b64encode(
            summary_text.encode('utf-8')).decode()
        pdf_output.seek(0)
        summary_pdf_b64 = base64.b64encode(pdf_output.read()).decode()
        file_base = f"executive_summary_{st.session_state['selected_campaign'].name.replace(' ', '_')}"
        st.markdown(f"""
<div style='display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap;'>
    <a download="{file_base}.txt" href="data:text/plain;base64,{summary_text_b64}" class="download-btn">📝 Download as Text</a>
    <a download="{file_base}.pdf" href="data:application/pdf;base64,{summary_pdf_b64}" class="download-btn">📄 Download as PDF</a>
</div>
<div class='footer' style='margin-top:1.5rem; color:#aaa; font-size:0.98rem;'>
    <b>Tip:</b> To save the summary as an image, use your device's screenshot feature.<br>
    <span style='font-size:0.93rem;'>On Mac: <code>Shift + Command + 4</code> | On Windows: <code>Windows + Shift + S</code></span>
</div>
        """, unsafe_allow_html=True)


if not (st.session_state.get('summary') and st.session_state.get('selected_campaign')):
    st.info("Select a campaign, customize the prompt if desired, and click 'Generate Executive Summary' to view the summary.")
st.markdown("---")
st.markdown("<div class='footer' style='color:#bbb; font-size:0.98rem; margin-top:1.5rem;'>Powered by GenAI | Designed with Streamlit</div>",
            unsafe_allow_html=True)
