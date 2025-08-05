import streamlit as st
import json
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@st.cache_resource
def get_driver():
    options = Options()
    # Uncomment below for background scraping
    # options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

def load_credentials():
    with open("config.json", "r") as f:
        config = json.load(f)
    return config["email"], config["password"]

def linkedin_login(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "username"))
    ).send_keys(email)

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "password"))
    ).send_keys(password)

    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
    ).click()
    time.sleep(3)

def scrape_jobs(driver, company_keyword, max_jobs=50):
    url = f"https://www.linkedin.com/jobs/search/?keywords={company_keyword}&location=India"
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list, ul.scaffold-layout__list-container"))
        )
    except:
        st.error("❌ Job list did not load.")
        return []

    # Scroll to load more jobs
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_list = soup.find("ul", class_="jobs-search__results-list") or soup.find("ul", class_="scaffold-layout__list-container")
    job_cards = job_list.find_all("li") if job_list else []

    jobs = []
    for card in job_cards[:max_jobs]:
        try:
            title = card.find("h3").get_text(strip=True)
            company = card.find("h4").get_text(strip=True)
            location = card.find("span", class_="job-search-card__location").get_text(strip=True)
            link = card.find("a", href=True)['href']
            date = card.find("time")["datetime"] if card.find("time") else "N/A"
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "date_posted": date,
                "link": link
            })
        except:
            continue

    return jobs

# ---------- Streamlit UI ----------
st.set_page_config(page_title="LinkedIn Job Scraper", layout="centered")
st.title("🔍 LinkedIn Job Scraper")

company_name = st.text_input("Enter Company Name (e.g., Google, TCS, Infosys)")
max_jobs = st.slider("Max Jobs", 5, 50, 10)

if st.button("Fetch Jobs"):
    if not company_name.strip():
        st.warning("⚠️ Please enter a valid company name.")
        st.stop()

    with st.spinner("Logging into LinkedIn..."):
        try:
            email, password = load_credentials()
            driver = get_driver()
            linkedin_login(driver, email, password)
        except Exception as e:
            st.error(f"❌ Login failed: {e}")
            driver.quit()
            st.stop()

    with st.spinner("Scraping job listings..."):
        jobs = scrape_jobs(driver, company_name.strip(), max_jobs=max_jobs)
        driver.quit()

    if not jobs:
        st.warning("No jobs found for that company.")
    else:
        st.success(f"✅ Found {len(jobs)} job(s)!")
        st.subheader("📋 Job Listings Table")
        df = pd.DataFrame(jobs)
        st.dataframe(df)

        st.subheader("🧾 JSON View")
        st.json(jobs)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="linkedin_jobs.csv", mime="text/csv")