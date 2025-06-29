# Interactive-Dashboard# Interactive Dashboard – Crime Incidents in Mexico

In this repository, you will find the code used to create an interactive dashboard based on criminal incident data in Mexico.  
The dashboard was built using Python, Streamlit and DuckDB, combining efficient data processing with dynamic visualizations.

---

## 🚀 Features

- Interactive filters by **state**, **year**, **month**, and **type of crime**
- Real-time queries using **DuckDB** on `.parquet` files
- Visualizations with **Plotly** and **Altair**
- Clean, responsive layout using **Streamlit**
- Data preprocessing and transformation steps included

---

## 🧰 Technologies Used

- Python 3.10+
- [Streamlit](https://streamlit.io/)
- [DuckDB](https://duckdb.org/)
- Pandas & Polars (optional processing)
- Plotly / Altair
- Parquet files for efficient data storage

---

## 📁 Project Structure

Interactive-Dashboard/
├── data/
│ ├── raw/ # Original CSV files
│ └── processed/ # Cleaned .parquet files
├── notebooks/ # EDA and transformation steps
├── dashboard_app.py # Main Streamlit dashboard
├── requirements.txt
└── README.md

---

## ⚙️ How to Run

1. **Clone the repo:**

```bash
git clone https://github.com/Roberto13-Vil/Interactive-Dashboard.git
cd Interactive-Dashboard
```

2. **Create virtual environment (optional):**

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

3. **Install dependencies:**

pip install -r requirements.txt

4. **Run the dashboard:**

streamlit run dashboard_app.py

## 🗃️ Data Source
The crime data comes from the [Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)](https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva), which publishes monthly records of reported crimes across Mexican states.

## ✍️ Author
Roberto Atonatiuh Solís Vilchis
Applied Mathematics & Computing – UNAM