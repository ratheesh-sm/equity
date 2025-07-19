import json
import os
from openai import OpenAI
import logging
from models import PromptTemplate

class LLMAnalyzer:
    """Service to analyze earnings transcripts using OpenAI's GPT models"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def analyze_transcript(self, transcript_text, company_name, quarter):
        """
        Analyze earnings transcript to extract key insights
        Returns structured analysis data
        """
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            
            # Get custom prompt from database or use default
            prompt_template = PromptTemplate.get_prompt('transcript_analysis')
            
            prompt = f"""
            {prompt_template.format(company_name=company_name, quarter=quarter)}

            Transcript:
            {transcript_text[:15000]}  # Limit text to stay within token limits
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional equity research analyst with expertise in financial analysis and earnings call interpretation. Provide detailed, actionable insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=2000,
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            self.logger.info(f"Successfully analyzed transcript for {company_name} {quarter}")
            return analysis
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing LLM response as JSON: {str(e)}")
            raise Exception("Failed to parse transcript analysis response")
        except Exception as e:
            self.logger.error(f"Error analyzing transcript: {str(e)}")
            raise Exception(f"Failed to analyze transcript: {str(e)}")
    
    def generate_executive_summary(self, financial_data, transcript_analysis, company_name, quarter):
        """
        Generate executive summary combining financial data and transcript insights
        """
        try:
            # Get custom prompt from database or use default
            prompt_template = PromptTemplate.get_prompt('executive_summary')
            
            prompt = f"""
            {prompt_template.format(company_name=company_name, quarter=quarter)}
            
            Financial Data Summary:
            {self._format_financial_data_for_prompt(financial_data)}
            
            Transcript Analysis:
            {json.dumps(transcript_analysis, indent=2)}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior equity research analyst writing for institutional investors."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {str(e)}")
            raise Exception(f"Failed to generate executive summary: {str(e)}")
    
    def enhance_risk_analysis(self, transcript_analysis, financial_data):
        """
        Generate enhanced risk analysis based on transcript and financial data
        """
        try:
            # Get custom prompt from database or use default
            prompt_template = PromptTemplate.get_prompt('risk_analysis')
            
            prompt = f"""
            {prompt_template}
            
            Transcript Analysis:
            {json.dumps(transcript_analysis, indent=2)}
            
            Financial Metrics:
            {self._format_financial_data_for_prompt(financial_data)}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a risk assessment specialist in equity research."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Error generating risk analysis: {str(e)}")
            return {
                "key_risks": ["Analysis unavailable"],
                "risk_mitigation": "Unable to assess",
                "positive_factors": ["Analysis unavailable"],
                "overall_risk_rating": "Unable to determine"
            }
    
    def _format_financial_data_for_prompt(self, financial_data):
        """Format financial data for inclusion in prompts"""
        if not financial_data or 'line_items' not in financial_data:
            return "No financial data available"
        
        formatted_data = []
        for item in financial_data['line_items'][:10]:  # Limit to top 10 items
            line = f"{item['line_item']}: "
            if item.get('previous_value'):
                line += f"Previous: {item['previous_value']:,.0f}, "
            if item.get('estimate'):
                line += f"Estimate: {item['estimate']:,.0f}"
            formatted_data.append(line)
        
        return "\n".join(formatted_data)
