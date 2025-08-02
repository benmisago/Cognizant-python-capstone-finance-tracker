from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB = 'expenses.db'

# Helper to connect to DB
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        category TEXT,
        amount REAL,
        date TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Home page — Add expense + recent
@app.route('/', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        category = request.form['category']
        try:
            amount = float(request.form['amount'])
        except ValueError:
            flash('Invalid amount.')
            return redirect(url_for('add_expense'))

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        conn.execute("INSERT INTO expenses (description, category, amount, date) VALUES (?, ?, ?, ?)",
                     (description, category, amount, date))
        conn.commit()
        conn.close()

        flash('Expense added!')
        return redirect(url_for('add_expense'))

    conn = get_db_connection()
    recent_expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT 10").fetchall()
    conn.close()

    return render_template('home.html', recent_expenses=recent_expenses)

# View all expenses
@app.route('/expenses')
def view_expenses():
    conn = get_db_connection()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC").fetchall()
    conn.close()
    return render_template('expenses.html', expenses=expenses)

# Summary by category
@app.route('/summary')
def view_summary():
    conn = get_db_connection()
    summary = conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category").fetchall()
    conn.close()
    return render_template('summary.html', summary=summary)

# Forecast page
@app.route('/forecast')
def view_forecast():
    conn = get_db_connection()
    rows = conn.execute("SELECT date, amount FROM expenses").fetchall()
    conn.close()

    today = datetime.now()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    weekly_total = 0
    monthly_total = 0

    for row in rows:
        try:
            row_date = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
            if row_date >= week_ago:
                weekly_total += row['amount']
            if row_date >= month_ago:
                monthly_total += row['amount']
        except (ValueError, TypeError):
            continue

    daily_avg = monthly_total / 30 if monthly_total else 0
    forecast = {
        'weekly': round(daily_avg * 7, 2),
        'monthly': round(daily_avg * 30, 2),
        'yearly': round(daily_avg * 365, 2)
    }

    return render_template('forecast.html', **forecast)

# Monthly Overview Page (organized by month & year)
@app.route('/monthly_overview', methods=['GET', 'POST'])
def monthly_overview():
    selected_month = request.args.get('month')
    selected_year = request.args.get('year')

    conn = get_db_connection()
    query = "SELECT description, category, amount, date FROM expenses"
    expenses = conn.execute(query).fetchall()
    conn.close()

    # Group expenses by month/year
    grouped = defaultdict(list)
    for exp in expenses:
        if exp['date']:
            date_obj = datetime.strptime(exp['date'], '%Y-%m-%d %H:%M:%S')
            month_name = date_obj.strftime('%B')
            year = str(date_obj.year)

            if (not selected_month or selected_month == month_name) and (not selected_year or selected_year == year):
                key = f"{month_name} {year}"
                grouped[key].append(exp)

    # Sort descending
    sorted_grouped = dict(sorted(grouped.items(), key=lambda x: datetime.strptime(x[0], '%B %Y'), reverse=True))

    # Generate unique months/years for dropdowns
    all_months = sorted({datetime.strptime(e['date'], '%Y-%m-%d %H:%M:%S').strftime('%B') for e in expenses})
    all_years = sorted({str(datetime.strptime(e['date'], '%Y-%m-%d %H:%M:%S').year) for e in expenses}, reverse=True)

    return render_template('monthly_overview.html',
                           grouped_expenses=sorted_grouped,
                           months=all_months,
                           years=all_years,
                           selected_month=selected_month,
                           selected_year=selected_year)

# Reset all expenses
@app.route('/reset')
def reset():
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses")
    conn.commit()
    conn.close()
    flash('All expenses have been deleted.')
    return redirect(url_for('add_expense'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
