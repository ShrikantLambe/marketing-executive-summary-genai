import streamlit as st
from data_ingestion.airtable_data import load_all_airtable
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity
from genai.summary import generate_summary


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


st.set_page_config(page_title="Executive Marketing Summary", layout="wide")
st.title("📊 Executive Marketing Summary Generator")
st.markdown(
    "Select a campaign to generate and view an executive-ready summary powered by GenAI.")


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
left_col, right_col = st.columns([1, 2])


with left_col:
    selected_campaign_name = st.selectbox(
        "Choose a Campaign", list(campaign_options.keys()), key="campaign_select_unique")
    if selected_campaign_name is None:
        st.warning("Please select a campaign.")
        st.stop()

    selected_campaign = campaign_options[selected_campaign_name]

    selected_attendees = [
        a for a in attendees if a.campaign_id == selected_campaign.id]
    selected_responses = [
        r for r in responses if r.campaign_id == selected_campaign.id]
    selected_activities = [
        a for a in activities if a.campaign_id == selected_campaign.id]
    selected_opportunities = [
        o for o in opportunities if o.campaign_id == selected_campaign.id]

    def build_default_prompt(attendees, opportunities):
        num_attendees = len(attendees)
        pipeline = sum(o.amount for o in opportunities)
        num_opps = len(opportunities)

        prompt = f'''
Please provide a bulleted executive summary for this campaign, including:
- Number of attendees
- Key contacts (do not list names in the prompt)
- Pipeline in room (sum of opportunity amounts)
- Number of opportunities
- Notable accounts and strategic context if available

Format the summary as clear bullet points with real numbers and, if possible, use actual attendee names from the data in the output.
'''
        return prompt


# --- UI logic (moved out of function) ---

    default_prompt = build_default_prompt(
        selected_attendees, selected_opportunities)
    user_prompt = st.text_area(
        "Additional Instructions for GenAI (customize summary)",
        value=default_prompt,
        height=250,
        key="prompt_input_unique"
    )
    generate = st.button("Generate Executive Summary",
                         key="generate_button_unique")

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

    # Store these for right_col
    st.session_state['selected_campaign'] = selected_campaign

with right_col:

    if st.session_state.get('summary') and st.session_state.get('selected_campaign'):
        # ...existing code for summary display, download buttons, PDF logic...
        campaign_name = st.session_state['selected_campaign'].name
        attendees_count = len(
            [a for a in attendees if a.campaign_id == st.session_state['selected_campaign'].id])
        pipeline_value = sum(getattr(
            o, 'amount', 0) for o in opportunities if o.campaign_id == st.session_state['selected_campaign'].id)
        pipeline_display = f"${pipeline_value/1e6:.1f}M" if pipeline_value else "$0.0M"
        key_account_ids = set(
            [o.account_id for o in opportunities if o.campaign_id == st.session_state['selected_campaign'].id])
        key_accounts = [
            a.name for a in accounts if a.id in key_account_ids]
        accounts_display = " ".join([
            f"<span style='background:#fff;padding:0.2rem 0.7rem;border-radius:0.7rem;color:#003c43;font-weight:600;margin-right:0.5rem;'>{a}</span>"
            for a in key_accounts[:4]
        ]) if key_accounts else "N/A"
        impact_lines = [line.lstrip('-').strip() for line in st.session_state['summary'].split(
            '\n') if line.strip() and not line.strip().startswith('Campaign:')]
        impact_html = "".join(
            [f"<li>{line}</li>" for line in impact_lines])
        st.markdown(
            f"""
<div id='executive-summary-card' style='background: linear-gradient(90deg, #0f2027, #2c5364); border-radius: 12px; padding: 2rem 2rem 1.5rem 2rem; color: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative;'>
    <div style='display: flex; align-items: center; justify-content: space-between;'>
        <h2 style='margin: 0; font-size: 1.6rem;'>Executive Summary</h2>
        <span style='background: #1de9b6; color: #003c43; font-weight: 600; border-radius: 1rem; padding: 0.3rem 1.2rem; font-size: 1rem;'>Generated</span>
    </div>
    <hr style='border: 1px solid #1de9b6; margin: 0.5rem 0 1.2rem 0;'>
    <div style='font-size: 1.1rem; margin-bottom: 0.7rem;'><b>Campaign:</b> {campaign_name}</div>
    <div style='display: flex; gap: 2.5rem; margin-bottom: 0.7rem;'>
        <div>👥 <b>{attendees_count}</b> Executives Attended</div>
        <div>💰 <b>{pipeline_display}</b> Pipeline Influence</div>
    </div>
    <div style='margin-bottom: 0.7rem;'><b>Key Accounts:</b> {accounts_display}</div>
    <div style='margin-bottom: 0.7rem;'><b>Strategic Impact</b></div>
    <ul style='margin: 0 0 0 1.2rem; padding: 0; color: #e0f7fa;'>
        {impact_html}
    </ul>
    <div style='display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap;'>
        <div id='dl-btn-txt'></div>
        <div id='dl-btn-pdf'></div>
        <div id='dl-btn-img'></div>
    </div>
</div>
                        """,
            unsafe_allow_html=True
    if st.session_state.get('summary') and st.session_state.get('selected_campaign'):
        st.subheader("Executive Summary")
        st.success(st.session_state['summary'])
        st.download_button(
            label="Download Summary as Text",
            data=st.session_state['summary'],
            file_name=f"executive_summary_{st.session_state['selected_campaign'].name.replace(' ', '_')}.txt",
            mime="text/plain"
        )
        from fpdf import FPDF
        import io

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

        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Campaign name
        pdf.section_title(f"Campaign: {campaign_name}")
        # Attendees and pipeline
        pdf.section_body(
            f"{attendees_count} Executives Attended    {pipeline_display} Pipeline Influence")
        # Key Accounts
        pdf.section_title("Key Accounts:")
        # Remove all <span ...> and </span> tags for PDF
        import re
        accounts_clean = re.sub(r"<span[^>]*>", "", accounts_display)
        accounts_clean = accounts_clean.replace("</span>", ", ").strip(', ')
        pdf.section_body(accounts_clean)
        # Strategic Impact
        pdf.section_title("Strategic Impact")
        pdf.bullet_list([line for line in impact_lines])

        pdf_bytes = pdf.output(dest='S').encode('latin1', errors='replace')
        pdf_output = io.BytesIO(pdf_bytes)

        import base64
        # Prepare text and PDF for download as base64
        summary_text = st.session_state['summary']
        summary_text_b64 = base64.b64encode(
            summary_text.encode('utf-8')).decode()
        pdf_output.seek(0)
        summary_pdf_b64 = base64.b64encode(pdf_output.read()).decode()
        file_base = f"executive_summary_{st.session_state['selected_campaign'].name.replace(' ', '_')}"
        st.markdown(f"""
<div style='display: flex; gap: 1rem; margin-top: 2rem; flex-wrap: wrap;'>
    <a download="{file_base}.txt" href="data:text/plain;base64,{summary_text_b64}" style="background: #1de9b6; color: #003c43; font-weight: 600; border: none; border-radius: 0.5rem; padding: 0.5rem 1.2rem; font-size: 1rem; cursor: pointer; text-decoration: none; display: inline-block;">Download Summary as Text</a>
    <a download="{file_base}.pdf" href="data:application/pdf;base64,{summary_pdf_b64}" style="background: #1de9b6; color: #003c43; font-weight: 600; border: none; border-radius: 0.5rem; padding: 0.5rem 1.2rem; font-size: 1rem; cursor: pointer; text-decoration: none; display: inline-block;">Download Summary as PDF</a>
</div>
<div style='margin-top: 0.7rem; color: #888; font-size: 0.98rem;'>
    <b>Tip:</b> To save the summary as an image, use your device's screenshot feature.<br>
    <span style='font-size:0.93rem;'>On Mac: <code>Shift + Command + 4</code> | On Windows: <code>Windows + Shift + S</code></span>
</div>
        """, unsafe_allow_html=True)

        # (Image download button and JS removed; replaced with screenshot tip above)
        st.download_button(
            label="Download Summary as PDF",
            data=pdf_output,
            file_name=f"executive_summary_{st.session_state['selected_campaign'].name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.info(
            "Select a campaign, customize the prompt if desired, and click 'Generate Executive Summary' to view the summary.")


st.markdown("---")
st.caption("Powered by GenAI | Designed with Streamlit")