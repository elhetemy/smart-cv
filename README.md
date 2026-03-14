# ⬡ CV.Studio — AI-Powered CV Builder

> Build, tailor, and export a professional CV in minutes — powered by Claude AI.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit)
![Anthropic](https://img.shields.io/badge/Powered%20by-Claude%20AI-7B61FF?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✦ What is CV.Studio?

CV.Studio is a local-first, AI-powered CV builder built with Python and Streamlit. Your CV data lives in a single `master_cv.json` file on your machine. The app gives you a live preview, an AI tailoring engine, a skills vault, and one-click PDF export — all in a clean dark UI.

---

## ✦ Features

| Feature | Description |
|---|---|
| **AI CV Tailor** | Paste any job description and Claude rewrites your summary and bullets to match it |
| **Live Preview** | See your CV update in real time as you edit |
| **Skills Vault** | Add, organize, and remove skills by category with one click |
| **AI Skill Gap Analyzer** | Paste a JD and get a list of missing skills you can add instantly |
| **PDF Export** | Download a clean, print-ready A4 PDF to send to recruiters |
| **Plain Text Export** | ATS-safe `.txt` version for online application forms |
| **JSON Export** | Backup or migrate your CV data anytime |
| **AI Cover Letter Generator** | Generate a personalized cover letter for any role in seconds |

---

## ✦ Screenshots

> _Add screenshots here after running the app locally._

---

## ✦ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/elhetemy/smart-cv-builder.git
cd smart-cv-builder
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Anthropic API key

> ⚠️ **The AI features (CV Tailor, Skill Gap Analyzer, Cover Letter Generator) require an Anthropic API key with an active paid tier.**
>
> Free-tier or trial keys will not work reliably for streaming responses.
>
> **Get your API key here → [console.anthropic.com](https://console.anthropic.com)**
> 1. Sign up or log in
> 2. Go to **API Keys** in the left sidebar
> 3. Click **Create Key** — copy it immediately, it's only shown once
> 4. Make sure your account is on a **paid plan** (Settings → Billing)

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> 🔒 The `.env` file is in `.gitignore` — your key will never be committed to GitHub.

### 5. Set up your CV data

Copy the template to create your personal CV file:

```bash
cp master_cv_template.json master_cv.json
```

> `master_cv.json` is also in `.gitignore` — your personal data stays local.

### 6. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ✦ Project Structure

```
smart-cv-builder/
├── app.py                    # Main Streamlit application
├── master_cv_template.json   # Template CV data (committed)
├── master_cv.json            # Your personal CV data (gitignored)
├── requirements.txt          # Python dependencies
├── .env                      # Your API key (gitignored)
├── .gitignore
└── README.md
```

---

## ✦ How the AI Features Work

All AI features use the **Claude API** via Anthropic's Python SDK with real-time streaming, so you see the response being written live.

- **CV Tailor** — sends your CV data + job description to Claude and gets back a tailored summary, rewritten bullets, matched skills, and strategic suggestions
- **Skill Gap Analyzer** — compares your current skill set against a JD and returns missing skills you can add to your CV with one click
- **Cover Letter Generator** — uses your CV data and the target role to write a personalized 3-paragraph cover letter

> 💡 Estimated API cost for personal use: **less than $1/month** given typical usage volume.

---

## ✦ Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | UI framework |
| `anthropic` | Claude AI API client |
| `reportlab` | PDF generation |
| `python-dotenv` | Load `.env` API key |

---

## ✦ Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## ✦ License

MIT License — feel free to use, modify, and distribute.

---

<p align="center">Built by <a href="https://github.com/elhetemy">Mohammed EL-Hetemy</a></p>
