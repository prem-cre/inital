import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("ce3b84871170b590f3430860428afa0764422d8ad61ea6bc9ad3554d4c82ba39")

def fetch_jobs_from_serpapi(query, location="India", limit=10):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "location": location,
        "api_key": SERPAPI_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "jobs_results" not in data:
        return []

    jobs = []
    for job in data["jobs_results"][:limit]:
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "posted": job.get("detected_extensions", {}).get("posted_at", "N/A"),
            "type": job.get("detected_extensions", {}).get("schedule_type", "N/A"),
            "via": job.get("via"),
            "link": job.get("apply_options", [{}])[0].get("link", job.get("job_id"))
        })

    return jobs


st.set_page_config(page_title="LinkedIn Jobs via SerpAPI", layout="centered")
st.title("🔍 LinkedIn Job Search")

if not SERPAPI_KEY:
    st.error("⚠️ Please set your SERPAPI_KEY in a .env file.")
    st.stop()

query = st.text_input("Enter job title or keyword (e.g., Software Engineer Google)")
location = st.text_input("Location", value="India")
limit = st.slider("Max results", 5, 20, 10)

if st.button("Search Jobs"):
    if not query:
        st.warning("Please enter a search keyword.")
        st.stop()

    with st.spinner("Fetching jobs from SerpAPI..."):
        jobs = fetch_jobs_from_serpapi(query, location, limit)

    if not jobs:
        st.warning("❌ No job listings found.")
    else:
        df = pd.DataFrame(jobs)
        st.success(f"✅ Found {len(jobs)} jobs!")
        st.dataframe(df)

        st.subheader("🔍 JSON View")
        st.json(jobs)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "serpapi_jobs.csv", "text/csv")
