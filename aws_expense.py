import boto3
from prometheus_client import start_http_server, Gauge
from datetime import datetime, timedelta, timezone
import time
import threading
import logging
import sys

# Initialize AWS client
ce_client = boto3.client('ce')

# Define Prometheus Gauges for AWS service expenses per user
gauges = {
    'weekly': Gauge('aws_user_weekly_expense', 'Weekly AWS User Expense', ['date', 'user']),
    'monthly': Gauge('aws_user_monthly_expense', 'Monthly AWS User Expense', ['date', 'user']),
    'fortnight': Gauge('aws_user_fortnight_expense', 'Fortnight AWS User Expense', ['date', 'user']),
    'today': Gauge('aws_user_today_expense', 'Today AWS User Expense', ['date', 'user'])
}

def get_user_expenses(start_date, end_date):
    """
    Get the AWS expenses by user from the Cost Explorer API within a specified period.
    Grouping is done by user tag (e.g., 'User').
    """
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'TAG',
                    'Key': 'User'  # Replace 'User' with your actual tag key
                }
            ]
        )
    except Exception as e:
        logging.error(f"Failed to fetch cost data: {e}")
        sys.exit(1)

    user_expenses = []
    for result in response['ResultsByTime']:
        date = result['TimePeriod']['Start']
        for group in result['Groups']:
            user = group['Keys'][0]  # The user name from the 'User' tag
            amount = float(group['Metrics']['BlendedCost']['Amount'])
            user_expenses.append({
                'Date': date,
                'User': user,
                'TotalAmount': amount
            })

    return user_expenses

def export_expenses_to_prometheus(start_days_ago, gauge_key):
    """
    Retrieve AWS user-wise expenses for a given period and expose them as Prometheus metrics.
    """
    end_date = datetime.now(timezone.utc).date().isoformat()
    start_date = (datetime.now(timezone.utc) - timedelta(days=start_days_ago)).date().isoformat()

    # Get expenses by user
    user_expenses = get_user_expenses(start_date, end_date)

    # Export each user expense as a Prometheus metric 
    for expense in user_expenses:
        date = expense['Date']
        user = expense['User']
        total_amount = expense['TotalAmount']
        # Set the value for the Prometheus gauge
        gauges[gauge_key].labels(date=date, user=user).set(total_amount)

def start_prometheus_server(port, start_days_ago, gauge_key, interval=900):
    """
    Start a Prometheus HTTP server on the specified port and export metrics at a regular interval.
    """
    try:
        start_http_server(port, addr="0.0.0.0")
        print(f"Prometheus server started at http://localhost:{port}/metrics for {gauge_key} user expenses")
    except Exception as e:
        logging.error(f"Failed to start Prometheus server on port {port}: {e}")
        sys.exit(1)

    while True:
        export_expenses_to_prometheus(start_days_ago, gauge_key)
        print(f"{gauge_key.capitalize()} user expense metrics exported.")
        time.sleep(interval)

if __name__ == "__main__":

    # Define the time periods for each server
    periods = {
        'weekly': 7,      # Last week (7 days)
        'monthly': 30,    # Last month (30 days)
        'fortnight': 14,  # Last 14 days (fortnight)
        'today': 1        # Today
    }

    # Start Prometheus servers on different ports for different metrics
    try:
        # Weekly expenses (last week) on port 3001
        threading.Thread(target=start_prometheus_server, args=(3001, periods['weekly'], 'weekly')).start()

        # Monthly expenses (last month) on port 3002
        threading.Thread(target=start_prometheus_server, args=(3002, periods['monthly'], 'monthly')).start()

        # Fortnightly expenses (last 14 days) on port 3003
        threading.Thread(target=start_prometheus_server, args=(3003, periods['fortnight'], 'fortnight')).start()

        # Today's expenses on port 3004
        threading.Thread(target=start_prometheus_server, args=(3004, periods['today'], 'today')).start()
        
    except Exception as e:
        logging.error(f"Failed to start Prometheus servers: {e}")
        sys.exit(1)
