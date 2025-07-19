from app import db
from datetime import datetime
import json

class ResearchSession(db.Model):
    """Model to store research session data across multiple steps"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    company_name = db.Column(db.String(255), nullable=True)
    quarter = db.Column(db.String(50), nullable=True)
    excel_filename = db.Column(db.String(255), nullable=True)
    pdf_filename = db.Column(db.String(255), nullable=True)
    summary_filename = db.Column(db.String(255), nullable=True)
    financial_data = db.Column(db.Text, nullable=True)  # JSON string
    transcript_analysis = db.Column(db.Text, nullable=True)  # JSON string
    final_report = db.Column(db.Text, nullable=True)
    current_step = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_financial_data(self, data):
        """Store financial data as JSON"""
        self.financial_data = json.dumps(data)
    
    def get_financial_data(self):
        """Retrieve financial data from JSON"""
        if self.financial_data:
            return json.loads(self.financial_data)
        return None
    
    def set_transcript_analysis(self, data):
        """Store transcript analysis as JSON"""
        self.transcript_analysis = json.dumps(data)
    
    def get_transcript_analysis(self):
        """Retrieve transcript analysis from JSON"""
        if self.transcript_analysis:
            return json.loads(self.transcript_analysis)
        return None

class PromptTemplate(db.Model):
    """Model to store customizable prompt templates"""
    id = db.Column(db.Integer, primary_key=True)
    step_name = db.Column(db.String(100), nullable=False, unique=True)
    prompt_text = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_prompt(step_name):
        """Get prompt for a specific step, return default if not found"""
        prompt = PromptTemplate.query.filter_by(step_name=step_name).first()
        if prompt:
            return prompt.prompt_text
        return PromptTemplate.get_default_prompt(step_name)
    
    @staticmethod
    def get_default_prompt(step_name):
        """Return default prompts for each step"""
        defaults = {
            'earning_summary': """You are a professional equity research analyst. Analyze the following quick earning summary for {company_name} ({quarter}) and extract key financial insights.

Please provide a structured analysis in JSON format with the following structure:
{{
    "key_metrics": "Summary of key financial metrics mentioned",
    "guidance_updates": "Any guidance changes or updates provided",
    "strategic_initiatives": "Key strategic initiatives or business updates",
    "market_position": "Commentary on market position and competitive dynamics",
    "management_tone": "Assessment of management confidence and outlook"
}}

Focus on:
- Revenue and earnings performance vs expectations
- Guidance changes and outlook
- Key business metrics and trends
- Strategic priorities and initiatives
- Management commentary and confidence""",
            
            'transcript_analysis': """You are a professional equity research analyst. Analyze the following earnings call transcript for {company_name} ({quarter}) and extract key insights.

Please provide a comprehensive analysis in JSON format with the following structure:
{{
    "management_commentary": "Key management statements and outlook",
    "strategic_themes": "Major strategic initiatives and business themes",
    "risks_and_tailwinds": "Identified risks and positive factors",
    "qa_insights": "Key insights from the Q&A session",
    "financial_highlights": "Notable financial metrics or guidance mentioned",
    "market_dynamics": "Commentary on market conditions and competitive landscape"
}}

Focus on:
- Forward-looking statements and guidance
- Strategic priorities and initiatives
- Risk factors and challenges
- Market opportunities and competitive positioning
- Management tone and confidence level
- Key financial metrics and performance drivers""",
            
            'executive_summary': """Create a concise executive summary for {company_name}'s {quarter} earnings analysis.

Provide a 2-3 paragraph executive summary that:
1. Highlights key financial performance vs estimates
2. Summarizes strategic themes and outlook
3. Identifies key investment considerations

Write in a professional, analyst-appropriate tone.""",
            
            'risk_analysis': """Based on the following transcript analysis and financial data, provide a detailed risk assessment:

Provide analysis in JSON format:
{{
    "key_risks": ["list of 3-5 key risks"],
    "risk_mitigation": "Management's approach to addressing risks",
    "positive_factors": ["list of 3-5 positive factors/tailwinds"],
    "overall_risk_rating": "Low/Medium/High with brief explanation"
}}""",
            
            'report_generation': """Generate a comprehensive equity research report combining financial data and transcript insights for {company_name} {quarter}."""
        }
        return defaults.get(step_name, "Default prompt not available")
