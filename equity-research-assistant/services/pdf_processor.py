import fitz  # PyMuPDF
import logging
import re

class PDFProcessor:
    """Service to extract text from PDF earnings transcripts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text(self, pdf_path):
        """
        Extract and clean text from PDF file
        Returns cleaned transcript text
        """
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            full_text = ""
            
            # Extract text from all pages
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                full_text += text + "\n\n"
            
            doc.close()
            
            # Clean and structure the text
            cleaned_text = self._clean_transcript_text(full_text)
            
            self.logger.info(f"Successfully extracted text from PDF: {pdf_path}")
            self.logger.debug(f"Extracted text length: {len(cleaned_text)} characters")
            
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {pdf_path}: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _clean_transcript_text(self, raw_text):
        """Clean and structure the extracted text"""
        try:
            # Remove excessive whitespace and normalize line breaks
            cleaned_text = re.sub(r'\n\s*\n', '\n\n', raw_text)
            cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
            
            # Remove common PDF artifacts
            cleaned_text = re.sub(r'Page \d+ of \d+', '', cleaned_text)
            cleaned_text = re.sub(r'©.*?(?=\n)', '', cleaned_text)
            
            # Fix common OCR issues
            cleaned_text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', cleaned_text)  # Fix hyphenated words
            
            # Ensure proper spacing around sentences
            cleaned_text = re.sub(r'\.(\w)', r'. \1', cleaned_text)
            cleaned_text = re.sub(r'\?(\w)', r'? \1', cleaned_text)
            cleaned_text = re.sub(r'!(\w)', r'! \1', cleaned_text)
            
            # Remove extra spaces
            cleaned_text = re.sub(r' +', ' ', cleaned_text)
            
            # Trim and ensure consistent line endings
            cleaned_text = cleaned_text.strip()
            
            return cleaned_text
            
        except Exception as e:
            self.logger.warning(f"Error cleaning transcript text: {str(e)}")
            return raw_text  # Return raw text if cleaning fails
    
    def extract_sections(self, text):
        """
        Extract common sections from earnings transcript
        Returns dict with identified sections
        """
        sections = {
            'prepared_remarks': '',
            'qa_session': '',
            'management_discussion': '',
            'forward_looking_statements': ''
        }
        
        try:
            # Common section indicators
            sections_patterns = {
                'prepared_remarks': [
                    r'prepared remarks',
                    r'opening remarks',
                    r'management discussion',
                    r'presentation'
                ],
                'qa_session': [
                    r'q&a',
                    r'question.?and.?answer',
                    r'questions and answers',
                    r'analyst questions'
                ],
                'forward_looking_statements': [
                    r'forward.?looking',
                    r'safe harbor',
                    r'disclaimer'
                ]
            }
            
            # Split text into potential sections
            paragraphs = text.split('\n\n')
            current_section = 'prepared_remarks'
            
            for paragraph in paragraphs:
                paragraph_lower = paragraph.lower()
                
                # Check if this paragraph indicates a new section
                for section_name, patterns in sections_patterns.items():
                    if any(pattern in paragraph_lower for pattern in patterns):
                        current_section = section_name
                        break
                
                # Add paragraph to current section
                if paragraph.strip():
                    sections[current_section] += paragraph + '\n\n'
            
            # Clean up sections
            for section_name in sections:
                sections[section_name] = sections[section_name].strip()
            
            return sections
            
        except Exception as e:
            self.logger.warning(f"Error extracting sections: {str(e)}")
            sections['prepared_remarks'] = text  # Put all text in prepared remarks as fallback
            return sections
