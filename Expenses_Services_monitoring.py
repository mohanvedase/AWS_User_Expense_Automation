import boto3
from prometheus_client import start_http_server, Gauge
from datetime import datetime, timezone
import time

# Initialize AWS clients
ce_client = boto3.client('ce')

# Define Prometheus Gauges for AWS expenses
expense_gauge = Gauge('aws_user_expense', 'Monthly AWS Expense', ['month'])

def get_monthly_expenses(start_date, end_date):
    """
    Get the monthly AWS expenses from Cost Explorer API.
    """
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost']
    )

    monthly_expenses = []
    for result in response['ResultsByTime']:
        month = result['TimePeriod']['Start']
        amount = float(result['Total']['BlendedCost']['Amount'])
        monthly_expenses.append({
            'Month': month,
            'TotalAmount': amount
        })

    return monthly_expenses

def export_expenses_to_prometheus():
    """
    Retrieve AWS expenses and expose them as Prometheus metrics.
    """
    start_date = '2023-01-01'  # Adjust start date
    end_date = datetime.now(timezone.utc).date().isoformat()

    # Get monthly expenses
    monthly_expenses = get_monthly_expenses(start_date, end_date)

    # Export each month as a Prometheus metric
    for expense in monthly_expenses:
        month = expense['Month']
        total_amount = expense['TotalAmount']
        # Set the value for the Prometheus gauge
        expense_gauge.labels(month=month).set(total_amount)

if __name__ == "__main__":
    # Start Prometheus server to expose metrics on port 8000
    start_http_server(8000)
    
    # Continuously export AWS expenses every hour (adjust as needed)
    while True:
        export_expenses_to_prometheus()
        time.sleep(3600)  # Wait for an hour before updating the data
