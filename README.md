# M&E Dashboard

An offline-capable Monitoring and Evaluation (M&E) dashboard application for tracking and analyzing project progress and impact.

## Features

- Logical Framework (LogFrame) Management
- Theory of Change (ToC) Visualization
- Results Framework Tracking
- Customizable Data Input Forms
- Interactive Data Visualization
- Automated Report Generation
- Advanced Data Analytics
- Trend Analysis
- Full Offline Functionality

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python init_db.py
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

```
melr/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
├── data/
├── tests/
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

## Usage

1. Access the application at `http://localhost:5000`
2. Create a new project or select an existing one
3. Set up your M&E framework (LogFrame, ToC, Results Framework)
4. Start collecting and analyzing data

## Development

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- Data Visualization: Plotly/Dash
- Offline Storage: IndexedDB

## License

MIT License 