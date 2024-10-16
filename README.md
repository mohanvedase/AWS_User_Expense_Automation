# AWS_User_Expense_Automation
# AWS User Expenses Automation with Boto3, Prometheus, and Grafana

## Overview
This project automates the monitoring and tracking of AWS user expenses using Boto3, Prometheus, and Grafana. The automation fetches expense data for individual users from AWS, exposes it as Prometheus metrics, and visualizes it using Grafana dashboards.

## Objective
The main goal is to create an automated system that:
- Tracks AWS expenses per user in real-time.
- Exposes expense data as metrics via Prometheus.
- Displays the data in Grafana dashboards for better visibility and cost monitoring.

## Key Components
1. **Boto3 (AWS SDK for Python)**
   - Fetches AWS user expenses using the Cost Explorer API.
2. **Prometheus**
   - Exposes the gathered expense data as metrics, which Prometheus scrapes periodically.
3. **Grafana**
   - Visualizes the metrics, allowing users to monitor expenses via interactive dashboards.

## Prerequisites
- An AWS account with IAM permissions to access the Cost Explorer API.
- Python environment with the following libraries:
  - `boto3`
  - `prometheus_client`
- A Prometheus server installed and configured to scrape metrics.
- A Grafana server installed and configured to display Prometheus data.

## Architecture Overview

### 1. Boto3 - AWS Expenses Fetching
- **Purpose**: Use Boto3 to interact with AWS Cost Explorer and retrieve daily user-specific expenses.
- **Details**:
  - Boto3 calls the `get_cost_and_usage` method of the Cost Explorer service.
  - The data fetched includes expenses grouped by user tags.

### 2. Prometheus Client - Metrics Exposure
- **Purpose**: Use the Prometheus Python client to expose expenses as metrics, which Prometheus scrapes.
- **Details**:
  - A gauge metric is created for each user, labeled by user and date.
  - Expenses are exposed in a Prometheus-friendly format for real-time monitoring.

### 3. Grafana - Dashboard Visualization
- **Purpose**: Configure Grafana to query Prometheus and display metrics through user-friendly dashboards.
- **Details**:
  - Users can view individual or aggregated expenses over time.
  - Dashboards support filters for user and date to customize the view.

## Step-by-Step Process

### 1. Setting Up Boto3 to Fetch AWS Expenses
- Configure AWS credentials on your local machine.
- Install Boto3:
  ```bash
  pip install boto3
  ```

### 2. Setting Up Prometheus to Expose Metrics
- Install the Prometheus Python client:
```bash
pip install prometheus_client
```
- Use the Prometheus Python client to expose the metrics in a Prometheus-friendly format.
```bash
python aws_expense.py
```
- ![code](https://github.com/user-attachments/assets/5da48fa1-9e36-440c-92a3-3be731b31f7a)

- Start the Prometheus server to scrape the metrics on a specified port (e.g., 3001).
- ![image](https://github.com/user-attachments/assets/ebc1f32c-56ff-4de4-8f13-2948440482bf)

### 3. Configuring Grafana Dashboards
- Install Grafana and set it up to pull data from Prometheus.
- Create dashboards with panels to visualize expenses.
- ![image](https://github.com/user-attachments/assets/66e5c0ca-b88a-419b-a8ee-b887699949e3)

- Add filters for user and date to focus on specific metrics.
### 4. Automation Workflow
- The script periodically fetches updated expense data from AWS.
- Prometheus scrapes the metrics every few minutes.
- Grafana displays the most recent expense data on the dashboards.

### Result
- You will get visualized dashboards in Grafana, showing user-specific expenses for each day, with options to filter by user and date.

### Conclusion
- This solution automates the collection of AWS user expenses, exposes the data as Prometheus metrics, and visualizes it using Grafana. This setup provides a clear view of user-specific expenses, helping with cost optimization and budgeting within an AWS account.
