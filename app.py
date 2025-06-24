# app.py
from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

# Load the sample dataset
df = pd.read_csv("ecommerce_transactions_sample.csv")

# Rule-based flagging logic
def flag_suspicious_transactions(data):
    suspicious = []
    for _, row in data.iterrows():
        reasons = []
        if row['amount'] > 50000:
            reasons.append("High amount")

        # Example: suspicious if multiple orders from same user in 2 minutes from different locations
        user_txns = data[data['user_id'] == row['user_id']]
        for _, other in user_txns.iterrows():
            if row['transaction_id'] != other['transaction_id']:
                time_diff = abs(pd.to_datetime(row['timestamp']) - pd.to_datetime(other['timestamp']))
                if time_diff < timedelta(minutes=2) and row['location'] != other['location']:
                    reasons.append("Rapid location switch")
                    break

        if reasons:
            suspicious.append({
                'transaction_id': row['transaction_id'],
                'user_id': row['user_id'],
                'timestamp': row['timestamp'],
                'amount': row['amount'],
                'location': row['location'],
                'device_id': row['device_id'],
                'ip_address': row['ip_address'],
                'reason': ", ".join(reasons)
            })

    return suspicious

@app.route('/')
def index():
    suspicious_txns = flag_suspicious_transactions(df)
    return render_template('index.html', transactions=suspicious_txns)

if __name__ == '__main__':
    app.run(debug=True)