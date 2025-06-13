import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from utils import (
    init_db,
    insert_transaction,
    load_data,
    # If you have these in utils, otherwise remove:
    # preprocess_data, forecast_expense, goal_progress, recommend_opportunities
    forecast_expense, goal_progress, recommend_opportunities
)

# Initialize the database
init_db()

st.set_page_config(page_title="Finance Tracker", layout="wide")
st.title("💸 Personal Finance Dashboard")

# Load data from SQLite
df = load_data()

# Sidebar
menu = st.sidebar.radio("Navigate", ["Dashboard", "Add Entry", "Forecast", "Goals", "Suggestions"])

# Dashboard
if menu == "Dashboard":
    st.header("📊 Expense Overview")
    exp = df[df['Type'] == 'Expense']
    income = df[df['Type'] == 'Income']

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Monthly Expenses")
        if not exp.empty:
            monthly_exp = exp.groupby('Month')['Amount'].sum().reset_index()
            fig = px.bar(monthly_exp, x='Month', y='Amount', title="Expenses per Month")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data found.")

    with col2:
        st.subheader("Expense Breakdown")
        if not exp.empty:
            pie = exp.groupby('Category')['Amount'].sum().reset_index()
            fig2 = px.pie(pie, names='Category', values='Amount', title="By Category")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense data found.")

# Add Entry
elif menu == "Add Entry":
    st.header("➕ Add New Entry")
    with st.form("entry_form"):
        date = st.date_input("Date")
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0)
        type_ = st.selectbox("Type", ["Expense", "Income"])
        desc = st.text_input("Description")
        submitted = st.form_submit_button("Add")
        if submitted:
            new_row = {
                "Date": pd.to_datetime(str(date)).strftime("%Y-%m-%d"),
                "Category": category,
                "Amount": float(amount),
                "Type": type_,
                "Description": desc
            }
            insert_transaction(new_row)
            st.success("Entry added successfully!")
            # Reload data after insert
            df = load_data()

# Forecast
elif menu == "Forecast":
    st.header("📈 6-Month Expense Forecast")
    hist, future = forecast_expense(df)
    fig3 = px.line(future, x="Month", y="Forecast", title="Forecasted Monthly Expenses")
    st.plotly_chart(fig3, use_container_width=True)

# Goals
elif menu == "Goals":
    st.header("🎯 Goal Tracker")
    goal = st.number_input("Set Savings Goal", value=100000)
    saved, percent = goal_progress(df, goal)
    st.metric("Total Savings", f"₹{saved:,.2f}")
    st.progress(min(int(percent), 100))

# Suggestions
elif menu == "Suggestions":
    st.header("💡 Earning Opportunities")
    recs = recommend_opportunities(df)
    if recs:
        for r in recs:
            st.info(r)
    else:
        st.success("No suggestions – your spending is optimized!")