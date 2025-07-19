# Equity Research Assistant

A Flask-based web application that automates equity research report generation by processing Excel files containing analyst estimates and PDF earnings transcripts using AI analysis.

## Features

- **Multi-step Workflow**: 3-step process for comprehensive research analysis
- **File Processing**: Upload and process Excel (.xlsx, .xls) and PDF files
- **AI Integration**: OpenAI GPT-4o for transcript analysis and report generation
- **Customizable Prompts**: Manage AI prompts for each analysis step
- **Report Export**: Generate downloadable PDF/Word documents
- **Dark Theme UI**: Professional Bootstrap-based interface

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- OpenAI API key (for AI analysis features)

## Installation & Setup

### 1. Download and Extract

Download the application files and extract to your desired directory.

### 2. Install Python Dependencies

```bash
# Navigate to the project directory
cd equity-research-assistant

# Install required packages
pip install flask flask-sqlalchemy gunicorn jinja2 openai openpyxl pandas psycopg2-binary pymupdf python-docx sqlalchemy weasyprint werkzeug beautifulsoup4 email-validator
```

### 3. Environment Setup

Create a `.env` file in the project root directory:

```bash
# Required for AI features
OPENAI_API_KEY=your_openai_api_key_here

# Flask session security (generate a random secret)
SESSION_SECRET=your_random_secret_key_here

# Optional: PostgreSQL database URL (defaults to SQLite if not provided)
# DATABASE_URL=postgresql://username:password@localhost/database_name
```

### 4. Create Required Directories

```bash
# Create upload and download directories
mkdir -p uploads downloads
```

### 5. Initialize Database

```bash
# Run database initialization
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
```

## Running the Application

### Development Mode

```bash
# Run with Flask development server
python main.py
```

### Production Mode

```bash
# Run with Gunicorn (recommended for production)
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

The application will be available at `http://localhost:5000`

## Usage Guide

### Step 0: Initial Setup
1. Enter company name and quarter
2. Upload Excel file with analyst estimates
3. Upload PDF earnings transcript

### Step 1: Earning Summary
1. Upload quick earning summary (optional)
2. Review and proceed to analysis

### Step 2: Transcript Analysis
1. AI processes the earnings transcript
2. Review and edit analysis results
3. Customize analysis prompts if needed

### Step 3: Report Generation
1. Generate comprehensive research report
2. Export as PDF or Word document
3. Download final report

## Customizing AI Prompts

Use the left sidebar "Prompt Manager" to customize AI analysis:

- **Earning Summary**: Process uploaded earning summaries
- **Transcript Analysis**: Analyze earnings call transcripts
- **Executive Summary**: Generate report summaries
- **Risk Analysis**: Identify risks and opportunities
- **Report Generation**: Final report compilation

## File Structure

```
equity-research-assistant/
├── app.py                 # Flask application setup
├── main.py               # Application entry point
├── models.py             # Database models
├── routes.py             # Route handlers
├── services/             # Business logic
│   ├── excel_processor.py
│   ├── pdf_processor.py
│   ├── llm_analyzer.py
│   └── report_generator.py
├── templates/            # HTML templates
├── static/              # CSS, JS, and assets
├── uploads/             # Uploaded files storage
├── downloads/           # Generated reports
└── instance/           # SQLite database (auto-created)
```

## Configuration

### Database Configuration
- **SQLite**: Default, no additional setup required
- **PostgreSQL**: Set `DATABASE_URL` environment variable

### File Upload Limits
- Maximum file size: 50MB
- Supported formats: Excel (.xlsx, .xls), PDF

### AI Configuration
- **Model**: OpenAI GPT-4o (latest model)
- **Response Format**: JSON for structured analysis
- **Token Limits**: Automatically managed

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install missing dependencies with pip
2. **Database errors**: Ensure database initialization was successful
3. **File upload fails**: Check file size limits and formats
4. **AI analysis fails**: Verify OpenAI API key is correctly set

### Error Logs

Check console output for detailed error messages. The application runs in debug mode by default for easier troubleshooting.

### Support

For technical issues:
1. Check error logs in the console
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed
4. Confirm file permissions for uploads/downloads directories

## Security Notes

- Keep your OpenAI API key secure and never commit it to version control
- Use a strong, random SESSION_SECRET for production deployments
- Consider using environment variable files (.env) that are not tracked by git
- Regular security updates for all dependencies are recommended

## License

This application is provided as-is for research and educational purposes.