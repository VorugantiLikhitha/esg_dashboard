# 🌍 ESG Emissions Intelligence Dashboard

An end-to-end AI-powered sustainability analytics platform built on EPA 
Greenhouse Gas Reporting Program (GHGRP) data spanning 14 years (2010–2023).

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)
![Plotly](https://img.shields.io/badge/Plotly-5.x-purple)
![Groq](https://img.shields.io/badge/AI-Groq%20Llama%203.3-green)
![EPA](https://img.shields.io/badge/Data-EPA%20GHGRP-orange)

---

## 📌 Overview

This dashboard enables sustainability analysts, ESG researchers, and data 
engineers to explore US industrial greenhouse gas emissions across facilities, 
states, industries, and years — with an AI assistant powered by Groq's 
Llama 3.3 model that answers questions directly from the data.

---

## 🧱 AI Tech Stack (Three-Layer Architecture)

### Infrastructure Layer
| Component | Technology |
|---|---|
| Local Development | MacOS / Python 3.12 |
| Data Storage | Local filesystem (EPA xlsx files) |
| Version Control | Git + GitHub |
| Environment | Python virtual environment (venv) |
| External Data API | EIA Energy Information Administration API |

### Model Layer
| Component | Technology |
|---|---|
| LLM Provider | Groq API (Llama 3.3 70B Versatile) |
| Data Context | Dynamic dataset summarization |
| Scope 2 Calculation | EPA eGRID emission factors |
| Scope 3 Estimation | EPA supply chain multipliers by industry |
| Data Processing | Pandas, NumPy |

### Application Layer
| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Visualizations | Plotly Express + Plotly Graph Objects |
| Geographic Maps | Plotly Choropleth + Density Mapbox |
| AI Chatbot | Groq API + context injection |
| Styling | Custom CSS + Google Fonts |

---

## 📊 Dashboard Pages

### 1. 📊 Overview
- KPI cards: Total facilities, emissions, top state, top industry
- Top 10 emitting states bar chart
- Sector breakdown donut chart
- Emissions over time trend line

### 2. 🏭 By Industry
- Horizontal bar chart — total emissions by sector
- Industry share pie chart
- Year-over-year industry trend lines

### 3. 📈 Trends
- Total emissions trend 2010–2023
- Top 5 states trend comparison
- Emission type breakdown (CO₂, CH₄, N₂O)

### 4. 🗺️ Heatmap
- US choropleth heatmap by state
- Facility-level density heatmap

### 5. 🌐 Scope 1 / 2 / 3
- **Scope 1** — Direct facility emissions (EPA GHGRP reported data)
- **Scope 2** — Estimated from electricity consumption × EPA eGRID factors
- **Scope 3** — Estimated using EPA supply chain multipliers by industry
- Scope distribution donut
- Year-over-year trend by scope
- Scope comparison by industry
- Top 10 states per scope

### 6. 🤖 AI Assistant
- Powered by Groq Llama 3.3 70B
- Context-aware: answers based on actual filtered dataset
- Chat memory across conversation
- Suggested quick questions

---

## 🔍 Filters (Sidebar)
- **Year Range** — Slider from 2010 to 2023
- **State** — All 50 US states
- **Industry Sector** — Power Plants, Oil & Gas, Chemicals, etc.
- **Emission Type** — Total, CO₂, CH₄, N₂O

All charts and AI context update dynamically based on filters.

---

## 📁 Project Structure

```
esg_dashboard/
├── app.py                  ← Main Streamlit application
├── data_loader.py          ← Data ingestion & cleaning (all 14 years)
├── scope_calculator.py     ← Scope 1/2/3 calculation engine
├── chatbot.py              ← Groq AI chatbot logic
├── data/                   ← EPA GHGRP xlsx files (not in repo)
│   ├── ghgp_data_2010.xlsx
│   ├── ghgp_data_2011.xlsx
│   │   ... (2010–2023)
│   └── ghgp_data_by_year_2023.xlsx
├── requirements.txt        ← Python dependencies
├── .env                    ← API keys (not in repo)
├── .gitignore
└── README.md
```

---

## 📦 Data Sources

| Source | Description | Access |
|---|---|---|
| EPA GHGRP | Direct facility emissions 2010–2023 | Free download |
| EPA eGRID | State-level grid emission factors | Free download |
| EIA API | Electricity consumption by state/sector | Free API key |
| Groq API | LLM inference (Llama 3.3) | Free tier |

**Dataset size:** 94,378 records · 8,778 unique facilities · 14 years

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.12+
- Groq API key (free at console.groq.com)
- EPA GHGRP data files

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/VorugantiLikhitha/esg_dashboard.git
cd esg_dashboard

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
touch .env
# Add: GROQ_API_KEY=your_key_here

# 5. Download EPA data
# Go to: https://www.epa.gov/ghgreporting/data-sets
# Download: 2023 Data Summary Spreadsheets
# Extract all xlsx files into data/ folder

# 6. Run the app
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🧠 Scope Calculation Methodology

### Scope 1 (Direct Emissions)
Source: EPA GHGRP reported data — facilities directly report CO₂, CH₄, 
and N₂O emissions to the EPA annually.

### Scope 2 (Indirect — Electricity)
```
Scope 2 = Electricity consumed (MWh) 
        × State grid emission factor (lb CO₂/MWh) [EPA eGRID]
        × 0.000453592 (lb → metric tons)
```
Electricity consumption estimated from industry-specific intensity factors.

### Scope 3 (Value Chain — Estimated)
```
Scope 3 = Scope 1 emissions × Industry multiplier
```
Multipliers based on EPA supply chain emission factors by sector.
Note: Real Scope 3 requires company-level value chain disclosure (CDP, etc.)

---

## 🚀 Scalability

### Current (Local)
- Single machine, local file storage
- Manual data refresh

### Production Scale
| Component | Scaled Solution |
|---|---|
| Data Storage | AWS S3 or Snowflake |
| Pipeline Orchestration | Apache Airflow |
| Processing | Apache Spark / Databricks |
| App Hosting | AWS EC2 or Streamlit Cloud |
| LLM | Claude API or fine-tuned model |
| Real-time data | Kafka streaming + EPA API |

---

## 👩‍💻 Author

**Likhitha Voruganti**  
MS Data Science | University of Houston  
Specialization: AI Engineering · Sustainability Data  
GitHub: [@VorugantiLikhitha](https://github.com/VorugantiLikhitha)

---

## 📄 License
MIT License — free to use, modify, and distribute.
