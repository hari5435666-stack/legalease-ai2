Python 3.14.2 (tags/v3.14.2:df79316, Dec  5 2025, 17:18:21) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
>>> import os
... import io
... import streamlit as st
... import google.generativeai as genai
... from docx import Document
... from dotenv import load_dotenv
... 
... # Load environment variables
... load_dotenv()
... 
... # Page configuration
... st.set_page_config(page_title="LegalEase - AI Legal Document Generator", page_icon="📜", layout="centered")
... 
... st.title("📜 LegalEase: AI-Powered Legal Document Generator")
... st.write("Generate customized legal drafts instantly using AI.")
... 
... # Sidebar for API Key input
... st.sidebar.header("Configuration")
... api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
... 
... if not api_key:
...     # Option to fall back to environment variable
...     api_key = os.getenv("GEMINI_API_KEY")
... 
... # Form inputs for the legal document
... st.subheader("Document Details")
... 
... doc_type = st.selectbox(
...     "Select Document Type",
...     ["Non-Disclosure Agreement (NDA)", "Rental Agreement", "Employment Contract", "Power of Attorney", "Custom Agreement"]
... )
... 
... party_a = st.text_input("First Party Name (e.g., Landlord / Employer / Company)")
... party_b = st.text_input("Second Party Name (e.g., Tenant / Employee / Client)")

jurisdiction = st.text_input("Governing Law / Jurisdiction (e.g., State of California, India)", value="General")

additional_details = st.text_area(
    "Key Terms & Conditions / Special Clauses",
    placeholder="e.g., Rent is $1,500/month, lease duration is 12 months, security deposit is $3,000..."
)

# Function to generate DOCX file in memory
def create_docx(text_content):
    doc = Document()
    doc.add_heading(f"{doc_type}", level=1)
    
    for paragraph in text_content.split('\n\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph.strip())
            
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# Generate Button
if st.button("Generate Legal Document", type="primary"):
    if not api_key:
        st.error("Please enter a valid Gemini API Key in the sidebar.")
    elif not party_a or not party_b:
        st.warning("Please provide names for both parties.")
    else:
        try:
            with st.spinner("Generating document draft using Gemini..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                prompt = f"""
                You are an expert legal draft writer. Generate a professional legal {doc_type}.
                
                Details:
                - Party A: {party_a}
                - Party B: {party_b}
                - Jurisdiction / Governing Law: {jurisdiction}
                - Specific Clauses / Provisions: {additional_details}

                Ensure the document includes standard sections such as:
                1. Title & Recitals
                2. Definitions
                3. Obligations & Rights
                4. Term & Termination
                5. Governing Law & Dispute Resolution
                6. Signature Blocks for both parties.

                Format clearly with standard legal wording.
                """

                response = model.generate_content(prompt)
                generated_text = response.text

                st.success("Document Generated Successfully!")
                st.subheader("Preview Document")
                st.markdown(generated_text)

                # Download Options
                docx_file = create_docx(generated_text)
                st.download_button(
                    label="📥 Download as Word (.docx)",
                    data=docx_file,
                    file_name=f"{doc_type.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
