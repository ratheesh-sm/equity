import os
import uuid
from flask import render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import ResearchSession, PromptTemplate
from services.excel_processor import ExcelProcessor
from services.pdf_processor import PDFProcessor
from services.llm_analyzer import LLMAnalyzer
from services.report_generator import ReportGenerator

# Allowed file extensions
ALLOWED_EXCEL_EXTENSIONS = {'xlsx', 'xls'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    """Step 0: Input collection"""
    # Initialize or get existing session
    if 'research_session_id' not in session:
        session['research_session_id'] = str(uuid.uuid4())
    
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session:
        research_session = ResearchSession(
            session_id=session['research_session_id'],
            current_step=0
        )
        db.session.add(research_session)
        db.session.commit()
    
    return render_template('index.html', session_data=research_session)

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads and basic info submission"""
    try:
        research_session = ResearchSession.query.filter_by(
            session_id=session['research_session_id']
        ).first()
        
        if not research_session:
            flash('Session expired. Please start over.', 'error')
            return redirect(url_for('index'))
        
        # Update basic info
        research_session.company_name = request.form.get('company_name', '').strip()
        research_session.quarter = request.form.get('quarter', '').strip()
        
        if not research_session.company_name or not research_session.quarter:
            flash('Company name and quarter are required.', 'error')
            return redirect(url_for('index'))
        
        # Handle Excel file upload
        excel_file = request.files.get('excel_file')
        if excel_file and excel_file.filename and allowed_file(excel_file.filename, ALLOWED_EXCEL_EXTENSIONS):
            excel_filename = secure_filename(f"{research_session.session_id}_{excel_file.filename}")
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_filename)
            excel_file.save(excel_path)
            research_session.excel_filename = excel_filename
        elif not research_session.excel_filename:
            flash('Please upload a valid Excel file (.xlsx or .xls).', 'error')
            return redirect(url_for('index'))
        
        # Handle PDF file upload
        pdf_file = request.files.get('pdf_file')
        if pdf_file and pdf_file.filename and allowed_file(pdf_file.filename, ALLOWED_PDF_EXTENSIONS):
            pdf_filename = secure_filename(f"{research_session.session_id}_{pdf_file.filename}")
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
            pdf_file.save(pdf_path)
            research_session.pdf_filename = pdf_filename
        elif not research_session.pdf_filename:
            flash('Please upload a valid PDF file.', 'error')
            return redirect(url_for('index'))
        
        research_session.current_step = 1
        db.session.commit()
        
        flash('Files uploaded successfully!', 'success')
        return redirect(url_for('step1'))
        
    except Exception as e:
        flash(f'Error uploading files: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/step1')
def step1():
    """Step 1: Process Excel and display financial data"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session or research_session.current_step < 1:
        flash('Please complete the previous step first.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Process Excel file if not already processed
        if not research_session.get_financial_data():
            excel_path = os.path.join(app.config['UPLOAD_FOLDER'], research_session.excel_filename)
            excel_processor = ExcelProcessor()
            financial_data = excel_processor.process_excel(excel_path)
            research_session.set_financial_data(financial_data)
            db.session.commit()
        
        financial_data = research_session.get_financial_data()
        return render_template('step1.html', 
                             session_data=research_session,
                             financial_data=financial_data)
        
    except Exception as e:
        flash(f'Error processing Excel file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/upload_earning_summary', methods=['POST'])
def upload_earning_summary():
    """Handle earning summary upload"""
    try:
        research_session = ResearchSession.query.filter_by(
            session_id=session['research_session_id']
        ).first()
        
        if not research_session:
            flash('Session expired. Please start over.', 'error')
            return redirect(url_for('index'))
        
        # Handle earning summary file upload
        summary_file = request.files.get('summary_file')
        if summary_file and summary_file.filename:
            # Define allowed extensions for summary files
            allowed_extensions = {'pdf', 'docx', 'doc', 'txt'}
            if allowed_file(summary_file.filename, allowed_extensions):
                summary_filename = secure_filename(f"{research_session.session_id}_summary_{summary_file.filename}")
                summary_path = os.path.join(app.config['UPLOAD_FOLDER'], summary_filename)
                summary_file.save(summary_path)
                
                # Store the summary filename in the database
                research_session.summary_filename = summary_filename
                db.session.commit()
                
                flash(f'Earning summary "{summary_file.filename}" uploaded successfully!', 'success')
            else:
                flash('Invalid file type. Please upload a PDF, Word, or Text file.', 'error')
        else:
            flash('Please select a file to upload.', 'error')
        
        return redirect(url_for('step1'))
        
    except Exception as e:
        flash(f'Error uploading earning summary: {str(e)}', 'error')
        return redirect(url_for('step1'))

@app.route('/approve_financial', methods=['POST'])
def approve_financial():
    """Approve financial data and move to step 2"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session:
        flash('Session expired. Please start over.', 'error')
        return redirect(url_for('index'))
    
    research_session.current_step = 2
    db.session.commit()
    
    return redirect(url_for('step2'))

@app.route('/step2')
def step2():
    """Step 2: Analyze PDF transcript"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session or research_session.current_step < 2:
        flash('Please complete the previous steps first.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Process PDF and analyze with LLM if not already done
        if not research_session.get_transcript_analysis():
            # Extract text from PDF
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], research_session.pdf_filename)
            pdf_processor = PDFProcessor()
            transcript_text = pdf_processor.extract_text(pdf_path)
            
            # Analyze with LLM
            llm_analyzer = LLMAnalyzer()
            analysis = llm_analyzer.analyze_transcript(
                transcript_text, 
                research_session.company_name,
                research_session.quarter
            )
            
            research_session.set_transcript_analysis(analysis)
            db.session.commit()
        
        transcript_analysis = research_session.get_transcript_analysis()
        return render_template('step2.html',
                             session_data=research_session,
                             transcript_analysis=transcript_analysis)
        
    except Exception as e:
        flash(f'Error analyzing transcript: {str(e)}', 'error')
        return redirect(url_for('step1'))

@app.route('/edit_analysis', methods=['POST'])
def edit_analysis():
    """Allow editing of transcript analysis"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session:
        return jsonify({'error': 'Session not found'}), 404
    
    try:
        # Update analysis with edited content
        analysis = research_session.get_transcript_analysis()
        analysis['management_commentary'] = request.form.get('management_commentary', '')
        analysis['strategic_themes'] = request.form.get('strategic_themes', '')
        analysis['risks_and_tailwinds'] = request.form.get('risks_and_tailwinds', '')
        analysis['qa_insights'] = request.form.get('qa_insights', '')
        
        research_session.set_transcript_analysis(analysis)
        db.session.commit()
        
        flash('Analysis updated successfully!', 'success')
        return redirect(url_for('step2'))
        
    except Exception as e:
        flash(f'Error updating analysis: {str(e)}', 'error')
        return redirect(url_for('step2'))

@app.route('/approve_analysis', methods=['POST'])
def approve_analysis():
    """Approve transcript analysis and move to step 3"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session:
        flash('Session expired. Please start over.', 'error')
        return redirect(url_for('index'))
    
    research_session.current_step = 3
    db.session.commit()
    
    return redirect(url_for('step3'))

@app.route('/step3')
def step3():
    """Step 3: Generate and preview final report"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session or research_session.current_step < 3:
        flash('Please complete the previous steps first.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Generate final report if not already done
        if not research_session.final_report:
            report_generator = ReportGenerator()
            final_report = report_generator.generate_report(
                company_name=research_session.company_name,
                quarter=research_session.quarter,
                financial_data=research_session.get_financial_data(),
                transcript_analysis=research_session.get_transcript_analysis()
            )
            
            research_session.final_report = final_report
            db.session.commit()
        
        return render_template('step3.html',
                             session_data=research_session,
                             final_report=research_session.final_report)
        
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')
        return redirect(url_for('step2'))

@app.route('/download_report/<format>')
def download_report(format):
    """Download the final report in specified format"""
    research_session = ResearchSession.query.filter_by(
        session_id=session['research_session_id']
    ).first()
    
    if not research_session or not research_session.final_report:
        flash('No report available for download.', 'error')
        return redirect(url_for('index'))
    
    try:
        report_generator = ReportGenerator()
        
        if format == 'pdf':
            file_path = report_generator.export_to_pdf(
                research_session.final_report,
                research_session.company_name,
                research_session.quarter,
                app.config['DOWNLOAD_FOLDER']
            )
        elif format == 'docx':
            file_path = report_generator.export_to_docx(
                research_session.final_report,
                research_session.company_name,
                research_session.quarter,
                app.config['DOWNLOAD_FOLDER']
            )
        else:
            flash('Invalid format requested.', 'error')
            return redirect(url_for('step3'))
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        flash(f'Error generating download: {str(e)}', 'error')
        return redirect(url_for('step3'))

@app.route('/reset')
def reset_session():
    """Reset the current session and start over"""
    if 'research_session_id' in session:
        research_session = ResearchSession.query.filter_by(
            session_id=session['research_session_id']
        ).first()
        if research_session:
            db.session.delete(research_session)
            db.session.commit()
        session.pop('research_session_id', None)
    
    flash('Session reset successfully.', 'info')
    return redirect(url_for('index'))

# Prompt Management Routes
@app.route('/prompts/edit/<step>')
def edit_prompts(step):
    """Edit prompts for a specific step"""
    prompt = PromptTemplate.query.filter_by(step_name=step).first()
    current_prompt = prompt.prompt_text if prompt else PromptTemplate.get_default_prompt(step)
    
    # Get step descriptions
    descriptions = {
        'earning_summary': 'Prompt used to process and analyze quick earning summaries uploaded in Step 1',
        'transcript_analysis': 'Prompt used to analyze earnings call transcripts and extract key insights',
        'executive_summary': 'Prompt used to generate executive summaries for reports',
        'risk_analysis': 'Prompt used to analyze risks and positive factors',
        'report_generation': 'Prompt used for overall report generation'
    }
    
    return render_template('edit_prompts.html', 
                         step=step, 
                         prompt_text=current_prompt,
                         description=descriptions.get(step, 'Custom prompt'),
                         is_default=prompt is None)

@app.route('/prompts/save/<step>', methods=['POST'])
def save_prompt(step):
    """Save edited prompt for a specific step"""
    try:
        prompt_text = request.form.get('prompt_text', '').strip()
        
        if not prompt_text:
            flash('Prompt text cannot be empty.', 'error')
            return redirect(url_for('edit_prompts', step=step))
        
        # Find existing prompt or create new one
        prompt = PromptTemplate.query.filter_by(step_name=step).first()
        
        if prompt:
            prompt.prompt_text = prompt_text
            prompt.is_default = False
        else:
            prompt = PromptTemplate(
                step_name=step,
                prompt_text=prompt_text,
                is_default=False
            )
            db.session.add(prompt)
        
        db.session.commit()
        flash(f'Prompt for {step} saved successfully!', 'success')
        
        return redirect(url_for('edit_prompts', step=step))
        
    except Exception as e:
        flash(f'Error saving prompt: {str(e)}', 'error')
        return redirect(url_for('edit_prompts', step=step))

@app.route('/prompts/reset')
def reset_prompts():
    """Reset all prompts to defaults"""
    try:
        # Delete all custom prompts
        PromptTemplate.query.delete()
        db.session.commit()
        
        flash('All prompts have been reset to defaults.', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error resetting prompts: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/prompts/preview/<step>')
def preview_prompt(step):
    """Preview how prompt will look with sample data"""
    prompt_text = PromptTemplate.get_prompt(step)
    
    # Sample data for preview
    sample_data = {
        'company_name': 'Sample Company Inc.',
        'quarter': 'Q3 2025'
    }
    
    try:
        formatted_prompt = prompt_text.format(**sample_data)
    except KeyError:
        formatted_prompt = prompt_text
    
    return jsonify({
        'formatted_prompt': formatted_prompt,
        'sample_data': sample_data
    })
