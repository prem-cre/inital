
import streamlit as st
import requests
import json

st.set_page_config(page_title="API Job Scraper", layout="centered")
st.title("🔍 Scrape Jobs via API")

url_input = st.text_input("Enter job search URL or keyword")
api_key = "4c88714d39msh83090877ecaffaep1d1466jsna69b2b4484fa"

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

def fetch_jobs_from_api(query):
    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            jobs = response.json().get("data", [])
            return jobs, None
        else:
            return [], f"API returned status {response.status_code}: {response.text}"
    except Exception as e:
        return [], str(e)

if st.button("🔍 Fetch Jobs"):
    if not url_input.strip():
        st.warning("⚠️ Please enter a valid search keyword.")
        st.stop()

    with st.spinner("Fetching job listings from API..."):
        job_data, error = fetch_jobs_from_api(url_input)

    if error:
        st.error(f"❌ Error fetching jobs: {error}")
    elif not job_data:
        st.info("ℹ️ No jobs found.")
    else:
        st.success("✅ Jobs found!")
        for job in job_data:
            st.markdown("---")
            st.markdown(f"**Title:** {job.get('job_title', 'N/A')}")
            st.markdown(f"**Company:** {job.get('employer_name', 'N/A')}")
            st.markdown(f"**Location:** {job.get('job_city', '')}, {job.get('job_country', '')}")
            st.markdown(f"**Posted:** {job.get('job_posted_at_datetime_utc', 'N/A')}")
            st.markdown(f"[View Job Posting]({job.get('job_apply_link', '#')})")
