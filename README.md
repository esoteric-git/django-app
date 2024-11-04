# Ocean Analytics Dashboard

A Django-based dashboard for visualizing ocean metrics including temperature, salinity, and depth measurements.

## 🌊 Features

- Real-time dashboard with temperature trends
- Detailed analytics view with multiple metrics
- PDF report generation
- Mock data generation for testing
- Admin interface for data management
- RESTful API endpoints for data access

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip
- virtualenv

### Installation

1. Clone the repository
```bash
git clone https://github.com/esoteric-git/django-app.git
cd django-app
```

2. Create and activate virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser
```bash
python manage.py createsuperuser
```

6. Generate mock data
```bash
python manage.py populate_mock_data
```

7. Run the development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to view the dashboard.

## 📊 Adding Data Manually

You can add data points directly to the database using SQLite commands:

1. Access SQLite console
```bash
python manage.py dbshell
```

2. Add a new data point (example)
```sql
INSERT INTO dashboard_oceanmetric (timestamp, location, temperature, salinity, depth)
VALUES (datetime('now'), 'Pacific Ocean', 25.5, 35.2, 1000);
```

3. Query recent data
```sql
SELECT * FROM dashboard_oceanmetric ORDER BY timestamp DESC LIMIT 5;
```

## 🔧 Project Structure

The main components of the project are:

- `dashboard/`: Main application directory
  - `views.py`: Contains the dashboard and analytics views
  - `models.py`: Database models for ocean metrics
  - `templates/`: HTML templates for the frontend
- `ocean_analytics/`: Project settings and configuration
- `static/`: Static files (CSS, JavaScript, images)

## 📝 API Documentation

The dashboard provides several endpoints:

- `/`: Main dashboard view
- `/analytics/`: Detailed analytics view
- `/admin/`: Admin interface
