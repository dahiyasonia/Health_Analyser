from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(page_title="Blood Work Analysis", layout="wide")

llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it")

st.markdown("""
<style>
.scroll-box{
            height: 230px;
            overflow-y:auto;
            padding: 12px 16px;
            border: 1px solid #333;
            border-radius: 8px;
            background-color: #1e1e1e;
            font-size: 0.9rem;
            line-height: 1.6;
} 
.scroll-box p, .scroll-box li{
            color: #e0e0e0;
}    
.section-label{
            font-size:1.1rem;
            font-weight:600;
            margin-bottom: 6px;
            color: #ffffff;
}                               
</style>
""", unsafe_allow_html=True)

st.title("Blood Work Analyser")

left_col, right_col = st.columns([1,1])

with left_col:
    st.subheader("Blood Work Report")
    blood_report = st.text_area(
        label="Paste your report below",
        height=500,
        placeholder="Paste your blood work report here....",
        label_visibility="collapsed"
    )
    analyze_clicked = st.button("Analyse",type="primary",use_container_width=True)

with right_col:
    st.subheader("Health Summary")
    health_box = st.empty()
    health_box.markdown('<div class="scroll-box"></div>', unsafe_allow_html=True)

    st.subheader("Suggested Diet Plan")
    diet_box = st.empty()
    diet_box.markdown('<div class="scroll-box"></div>', unsafe_allow_html=True)

if analyze_clicked:
    if not blood_report.strip():
        with left_col:
            st.warning("Please paste a blood work report before analyzing.")
    else:
        with st.spinner("Analysing your blood work..."):

            #Stage1: Extract and flag abnormal values
            extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract all test values and classify each one as HIGH, LOW, or NORMAL
based on the reference ranges provided in the report.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | References: range

Blood Report:
{blood_report}
"""
            extraction_response = llm.invoke(extraction_prompt)
            extracted_values = extraction_response.text

            # Stage2: Health summary and Indian Diet plan
            diet_prompt=f"""
You are a clinical nutritionist specalising the Indian dietary plan.diet_box

Based on the blood work analysis below, provide two clearly separated sections:

Section 1 - Health Summary:
Write 4-5 lines explaining the patient's condition in simple, non-technical language.

Section-2 - Indian Diet Plan:
List foods to eat more of and eat foods to avoid, using commonly available Indian foods
like dal, sabzi, roti, rice, etc. Keep it practical and concise.set

Blood work Analysis:
{extracted_values}
"""
            diet_response = llm.invoke(diet_prompt)
            full_response = diet_response.text

            #Split responses into two sections
            if "Section 2" in full_response:
                parts=full_response.split("Section 2")
                health_summary = parts[0].replace("Section 1-Health Summary: ","").replace("Section 1","").strip()
                diet_plan = ("Section 2" + parts[1]).replace("Section 2 - INDIAN DIET PLAN:","".replace("SECTION 2",""))
            else:
                health_summary = full_response
                diet_plan =""

            #Render into fixed-height scrollable boxes
            health_box.markdown(
                f'<div class="scroll-box">{health_summary}</div>',
                unsafe_allow_html=True
            )  
            diet_box.markdown(
                f'<div class="scroll-box">{diet_plan if diet_plan else full_response}</div>',
                unsafe_allow_html=True
            )  
            