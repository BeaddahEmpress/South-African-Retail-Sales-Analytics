South African Retail Sales Analytics

📌 Project Overview

Retail businesses generate valuable data through everyday sales transactions. Analysing this data helps businesses understand customer purchasing patterns, monitor revenue, identify top-performing products, and make informed decisions.

South African Retail Sales Analytics is a data analytics project designed to explore retail sales data and transform raw transaction records into meaningful business insights using Python, SQL, cloud database technology, and interactive visualisation.

The project demonstrates an end-to-end data workflow, from dataset preparation and database management to analytical querying and dashboard development.

🎯 Project Objectives

- Analyse retail sales performance using transaction-level data.
- Evaluate revenue and sales trends across products, categories, and other available business dimensions.
- Identify top-performing products and categories.
- Explore changes in sales performance over time.
- Use SQL to retrieve and aggregate business data.
- Build an interactive dashboard to communicate findings clearly.

🛠️ Tools and Technologies

- Python — data processing and analysis
- Pandas — data cleaning and manipulation
- SQL — querying and aggregating retail data
- Supabase — cloud-based PostgreSQL database
- Streamlit — interactive dashboard development
- Plotly — interactive data visualisation
- CSV — source dataset

📂 Dataset

The project uses a retail sales dataset containing transaction records for analysis.

Depending on the available dataset fields, the analysis can explore:

- Transaction dates
- Product names or categories
- Quantities sold
- Sales amounts or revenue
- Customer or location information, where available

The dataset is used to demonstrate practical retail analytics workflows. Refer to the source dataset and project code for the exact column names and definitions.

🔄 Project Workflow

1. Data Preparation

Load the retail dataset using Pandas, inspect its structure, check data types, and prepare the data for analysis.

2. Cloud Database Integration

Store the prepared data in a Supabase PostgreSQL database to support structured queries and cloud-based data access.

3. SQL Analysis

Use SQL queries to aggregate sales, compare performance across available categories, and examine trends over time.

4. Data Visualisation

Use Plotly to create interactive charts that make sales patterns and performance differences easier to understand.

5. Dashboard Development

Develop a Streamlit dashboard that presents key metrics, charts, and analytical findings in an accessible format.

📊 Key Business Questions

This project is designed to investigate questions such as:

- What is the total revenue generated during the period covered by the dataset?
- Which products or categories contribute the most to sales?
- How do sales change over time?
- Which categories have the strongest sales performance?
- What patterns could help a retail business improve its sales strategy?

The answers depend on the actual dataset and the results produced by the analysis.

💼 Business Value

Retail sales analytics can support better business decisions by helping organisations:

- Monitor revenue and sales performance.
- Identify high-performing products and categories.
- Understand sales trends.
- Recognise areas that may need further investigation.
- Make more informed inventory, marketing, and sales planning decisions.

🚀 Running the Project Locally

Prerequisites

Install Python and the required project dependencies.

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER

Replace the placeholders with your actual GitHub repository URL and folder name.

2. Install dependencies

pip install streamlit pandas plotly supabase

Install any additional packages required by your code.

3. Configure Supabase

Create a ".streamlit/secrets.toml" file locally and configure your Supabase connection credentials according to the application's code.

Security reminder: Never commit "secrets.toml", database passwords, or API keys to GitHub.

4. Run the dashboard

streamlit run app.py

Streamlit should launch the dashboard in your browser.

📁 Project Structure

South-African-Retail-Sales-Analytics/
├── app.py
├── south_african_retail_sales.csv
├── README.md
└── .streamlit/
    └── secrets.toml

This is an example structure. Adjust the filenames to match your actual project. Keep private credentials out of the public repository.

👩🏽‍💻 Author

Lerato Motloung

Data Engineer focused on building practical data solutions using Python, SQL, PostgreSQL, cloud technologies, and data visualisation.

This project demonstrates my interest in transforming raw data into useful business insights through data preparation, database querying, and interactive analytics.

---

This project is intended for educational and portfolio purposes.
