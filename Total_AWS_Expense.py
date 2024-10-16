import boto3
from prometheus_client import start_http_server, Gauge
from datetime import datetime, timezone
import time
import threading
import logging
import sys

# Initialize AWS client
ce_client = boto3.client('ce')

# Define Prometheus Gauge for total AWS expenses per user
gauge = Gauge('aws_user_total_expense', 'Total AWS User Expense', ['user'])

def get_user_expenses(start_date, end_date):
    """
    Get the AWS expenses by user from the Cost Explorer API for the entire billing period.
    Grouping is done by user tag (e.g., 'User'), handling pagination manually.
    """
    user_expenses = {}
    next_token = None

    try:
        while True:
            # Prepare the request parameters
            params = {
                'TimePeriod': {
                    'Start': start_date,
                    'End': end_date
                },
                'Granularity': 'MONTHLY',  # Change to MONTHLY for consolidated view
                'Metrics': ['BlendedCost'],
                'GroupBy': [
                    {
                        'Type': 'TAG',
                        'Key': 'User'  # Replace 'User' with your actual tag key
                    }
                ]
            }

            # Only include NextPageToken if it's not None
            if next_token:
                params['NextPageToken'] = next_token

            # Request the AWS Cost Explorer API
            response = ce_client.get_cost_and_usage(**params)

            # Iterate through the results and store them
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    user = group['Keys'][0]  # The user name from the 'User' tag
                    amount = float(group['Metrics']['BlendedCost']['Amount'])
                    
                    # Aggregate the expenses by user
                    if user in user_expenses:
                        user_expenses[user] += amount
                    else:
                        user_expenses[user] = amount

            # Check if there is a next page
            next_token = response.get('NextPageToken')
            if not next_token:
                break  # No more pages

    except Exception as e:
        logging.error(f"Failed to fetch cost data: {e}")
        sys.exit(1)

    return user_expenses

def export_expenses_to_prometheus():
    """
    Retrieve AWS user-wise expenses for the entire billing period and expose them as Prometheus metrics.
    """
    # Set the start date as the earliest possible date for billing data.
    start_date = '2024-05-05'  # You can adjust this date to any earlier period
    end_date = datetime.now(timezone.utc).date().isoformat()

    # Get expenses by user
    user_expenses = get_user_expenses(start_date, end_date)

    # Export each user expense as a Prometheus metric
    for user, total_amount in user_expenses.items():
        # Set the value for the Prometheus gauge
        gauge.labels(user=user).set(total_amount)
        logging.info(f"Exported metrics: User={user}, TotalAmount={total_amount}")

def start_prometheus_server(port, interval=900):
    """
    Start a Prometheus HTTP server on the specified port and export metrics at a regular interval.
    """
    try:
        start_http_server(port, addr="0.0.0.0")
        print(f"Prometheus server started at http://localhost:{port}/metrics for total user expenses")
    except Exception as e:
        logging.error(f"Failed to start Prometheus server on port {port}: {e}")
        sys.exit(1)

    while True:
        export_expenses_to_prometheus()
        print("User expense metrics exported.")
        time.sleep(interval)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Start Prometheus server on port 5002 for all users' expenses
    try:
        threading.Thread(target=start_prometheus_server, args=(5002,)).start()
    except Exception as e: 
        logging.error(f"Failed to start Prometheus server: {e}")
