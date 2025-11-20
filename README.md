# 📄 Resume NLP Parser using Streamlit & Python

> **AI-powered Resume Parsing System** that extracts candidate information from PDF resumes using NLP, evaluates resume quality, and suggests improvements based on desired job roles.

---

## 🚀 Features

✔️ Upload PDF resume in UI
✔️ Extracts:

* 👤 **Name**
* 📧 Email
* 📱 Phone Number
* 🎓 Education
* 🧠 Skills
* 💼 Experience Level
* 📊 Resume Score (/100)

✔️ Suggests missing skills based on job title
✔️ Saves uploaded resumes to SQLite database
✔️ Admin panel to view feedback & stored resumes
✔️ Recruiter mode for resume evaluation

---

## 🏗 Project Architecture

```
Resume-NLP-Parser/
│
├── main.py                         # Application entry point
│
├── modules/
│   ├── users.py                    # User side parsing interface
│   ├── recruiters.py               # Recruiter evaluation UI
│   └── admin.py                   # Admin dashboard
│
├── resume_parser.py                # Core NLP logic
│
├── data/
│   ├── newSkills.csv               # Skills dictionary
│   ├── feedback_data.csv           # Admin feedback storage
│   └── user_pdfs.db                # SQLite DB (resume storage)
│
├── venv/                           # Virtual env
└── requirements.txt                # Dependencies
```

---

## 🧠 Technologies Used

| Domain        | Tools              |
| ------------- | ------------------ |
| NLP           | spaCy, NLTK, Regex |
| UI            | Streamlit          |
| PDF Parsing   | PyMuPDF (fitz)     |
| Storage       | SQLite             |
| Data Handling | pandas             |
| Language      | Python             |

---

## 🔍 How NLP Is Used

| NLP Task             | Implementation                       |
| -------------------- | ------------------------------------ |
| Text extraction      | PyMuPDF                              |
| Tokenization         | NLTK                                 |
| Name Extraction      | spaCy NER                            |
| Skill Extraction     | Keyword matching + NLP preprocessing |
| Experience Detection | Regex + heuristics                   |
| Education Parsing    | Pattern matching                     |
| Resume Score         | Rule-based evaluation                |

---

## ⚙️ Setup Instructions

```bash
# Clone the repository
git clone https://github.com/yourusername/Resume-NLP-Parser.git
cd Resume-NLP-Parser

# Create Virtual Environment
python -m venv venv
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm

# Run the application
streamlit run main.py
```

---

## 📊 Resume Score Calculation (Current Logic)

| Section      | Weight  |
| ------------ | ------- |
| Name         | 10      |
| Email        | 10      |
| Phone Number | 10      |
| Education    | 20      |
| Skills       | 30      |
| Experience   | 20      |
| **Total**    | **100** |

➡ Score based on **information completeness**, not content quality.

---

## 🚀 Future Improvements

* ML-based resume quality prediction
* Job-role based scoring using NLP embeddings (BERT/SentenceTransformer)
* Add project & certification evaluation
* ATS optimization score
* Resume formatting and grammar quality detection

---

## 🔐 Admin Panel

* Views uploaded resumes
* Reads feedback from `feedback_data.csv`
* Supports malformed row handling

---

## 🎯 Project Summary

> “This project converts unstructured resume PDFs into structured insights using classical NLP techniques and rule-based extraction. It helps recruiters evaluate resumes faster and enables candidates to improve their resumes based on job-relevant suggestions.”

---

## 🟢 License

MIT License

---

## ⭐ Contribution

Pull requests are welcome!
If you'd like to enhance resume scoring logic or add deep-learning based NLP, feel free to open an issue 🚀

---

Would you like:
📌 A **project abstract (150 words)** for report submission?
📌 A **diagram / architecture image** for viva/presentation?
📌 Or a **Future Scope slide content**?

Just say **"give abstract"** or **"give diagram"** 💡
