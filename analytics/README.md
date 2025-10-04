# Analytics Directory

This directory contains analytics tools for analyzing the Q&A application data from both SQLite database and JSON log files.

## Files

### 1. `events_per_day.sql`
SQL queries for analyzing events per day from the SQLite database.

**Features:**
- Basic events per day count with unique users
- Last 30 days analysis with averages
- Running totals and cumulative statistics
- Top 10 most active days
- Weekly and monthly aggregations

**Usage:**
```bash
# Connect to the database and run queries
sqlite3 ../server/data/qa_database.db < events_per_day.sql

# Or run specific queries
sqlite3 ../server/data/qa_database.db "SELECT DATE(timestamp) as event_date, COUNT(*) as event_count FROM events GROUP BY DATE(timestamp) ORDER BY event_date DESC;"
```

### 2. `questions_per_user.py`
Python script for analyzing user question patterns from JSON log files.

**Features:**
- Questions per user from event logs
- User statistics from users.json file
- Activity pattern analysis (peak hours, most active days)
- Data comparison between JSON and database sources
- CSV export functionality
- Comprehensive reporting

**Usage:**
```bash
# Run the analysis script
cd /Users/menachem/projects/project_one/analytics
python questions_per_user.py

# Or run from any directory
python /Users/menachem/projects/project_one/analytics/questions_per_user.py
```

**Output:**
- Console report with detailed user statistics
- CSV file: `questions_per_user.csv` with exportable data

## Data Sources

### SQLite Database (`../server/data/qa_database.db`)
- **users** table: User registration and metadata
- **events** table: Question/answer events with timestamps

### JSON Files (`../server/data/`)
- **users.json**: User information and statistics
- **events/events_YYYY-MM-DD.json**: Daily event logs

## Sample Queries and Analysis

### SQL Examples:
```sql
-- Events per day for last 7 days
SELECT
    DATE(timestamp) as date,
    COUNT(*) as events,
    COUNT(DISTINCT username) as unique_users
FROM events
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Top active users
SELECT
    username,
    COUNT(*) as total_questions,
    MIN(DATE(timestamp)) as first_question,
    MAX(DATE(timestamp)) as last_question
FROM events
GROUP BY username
ORDER BY total_questions DESC
LIMIT 10;
```

### Python Examples:
```python
# Import and use the analyzer
from questions_per_user import QuestionsPerUserAnalyzer

analyzer = QuestionsPerUserAnalyzer()
questions_per_user = analyzer.get_questions_per_user()
print(f"Total users: {len(questions_per_user)}")

# Generate full report
report = analyzer.generate_report()
print(report)

# Export to CSV
analyzer.export_to_csv("my_export.csv")
```

## Requirements

### For SQL queries:
- SQLite3 (usually pre-installed)
- Access to the database file

### For Python script:
- Python 3.6+
- Access to the server modules (json_logger)
- JSON data files in the expected structure

## Troubleshooting

1. **"Could not import JSONLogger" error**:
   - Make sure you're running the Python script from the analytics directory
   - Verify the server directory exists and contains json_logger.py

2. **"No data found" messages**:
   - Check if the server has been running and generating data
   - Verify the data directory exists: `../server/data/`

3. **SQLite database not found**:
   - Ensure the server has been initialized at least once
   - Check the path: `../server/data/qa_database.db`

## Integration with Server

These analytics tools are designed to work alongside the running Q&A server:

1. **Real-time analysis**: Run while server is active to get current data
2. **Historical analysis**: Analyze accumulated data from past sessions
3. **Monitoring**: Use for ongoing system monitoring and insights

## Future Enhancements

Potential additions to the analytics suite:
- Interactive web dashboard
- Automated reporting schedules
- Performance metrics analysis
- User behavior patterns
- System health monitoring
- Data visualization charts
