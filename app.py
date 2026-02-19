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
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'Executive Summary', ln=True, align='C')
                self.ln(10)
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)

        def clean_text(text):
            replacements = {
                '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
                '\u2013': '-', '\u2014': '-', '\u2026': '...', '\u00a0': ' '
            }
            for orig, repl in replacements.items():
                text = text.replace(orig, repl)
            return text.encode('latin1', errors='replace').decode('latin1')
        for line in st.session_state['summary'].split('\n'):
            pdf.multi_cell(0, 10, clean_text(line))
        pdf_bytes = pdf.output(dest='S').encode('latin1', errors='replace')
        pdf_output = io.BytesIO(pdf_bytes)
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