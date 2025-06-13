import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
 
DB_FILE = "finance.db"
 
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT,
            Category TEXT,
            Amount REAL,
            Type TEXT,
            Description TEXT
        )
    ''')
    conn.commit()
    conn.close()
 
def insert_transaction(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (Date, Category, Amount, Type, Description)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['Date'], data['Category'], data['Amount'], data['Type'], data['Description']))
    conn.commit()
    conn.close()
 
def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df
def preprocess_data(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    return df

def forecast_expense(df):
    df = df[df['Type'] == 'Expense']
    monthly = df.groupby('Month')['Amount'].sum().reset_index()
    monthly['Month'] = monthly['Month'].astype(str)
    monthly['Month'] = pd.to_datetime(monthly['Month'])

    monthly['Month_Num'] = range(len(monthly))
    X = monthly[['Month_Num']]
    y = monthly['Amount']

    model = LinearRegression()
    model.fit(X, y)

    future = pd.DataFrame({'Month_Num': range(len(monthly), len(monthly)+6)})
    future['Forecast'] = model.predict(future[['Month_Num']])
    future['Month'] = pd.date_range(start=monthly['Month'].max()+pd.offsets.MonthBegin(1), periods=6, freq='MS')

    return monthly, future

def goal_progress(df, goal=100000):
    savings = df[df['Type'] == 'Income']['Amount'].sum() - df[df['Type'] == 'Expense']['Amount'].sum()
    percent = (savings / goal) * 100
    return savings, percent

def recommend_opportunities(df):
    recs = []
    if df[df['Category'] == 'Mobile Recharge']['Amount'].mean() > 250:
        recs.append("Consider switching to a cheaper mobile plan.")
    if df[df['Category'] == 'Groceries']['Amount'].mean() > 1000:
        recs.append("Look for monthly grocery deals or local markets.")
    return recs