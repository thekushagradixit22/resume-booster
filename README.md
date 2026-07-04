# 🚀 Resume Booster

Resume Booster is a Streamlit-based web application that leverages Google's **Gemini API (Free Tier)** to analyze how well your resume matches a target job description. The application evaluates your profile the same way a modern Applicant Tracking System (ATS) and recruiter would, providing actionable insights to optimize your resume.

---

## 🛠️ How It Works

1. **Upload Your Resume:** Drop in your resume in **PDF** format.
2. **Paste the Job Description:** Input the target role's requirements.
3. **Analyze:** Click the **"Analyze Resume"** button.
4. **Get Insights:** Instantly review your overall ATS match score, keyword gaps, and tailored optimization tips.

---

## ✨ Features

* **AI-Powered Analysis:** Uses Gemini's advanced text processing to simulate an ATS scanner.
* **Keyword & Skill Gap Analysis:** Identifies critical industry keywords and skills missing from your resume.
* **Instant ATS Score:** Gives a transparent percentage match based on the job description.
* **Fast & Interactive UI:** Built completely on Streamlit for a seamless user experience.

---

## 💻 Tech Stack

* **Frontend & UI:** Streamlit
* **Core LLM Engine:** Google Gemini API (`google-generativeai`)
* **Language:** Python 3.x
* **Document Processing:** PyPDF2 / pdfplumber (or your chosen PDF parser)

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites
Ensure you have Python installed. You will also need a **Gemini API Key** (you can get one for free from Google AI Studio).

### 2. Clone the Repository
```bash
git clone [https://github.com/thekushagradixit22/resume-booster.git](https://github.com/thekushagradixit22/resume-booster.git)
cd resume-booster
