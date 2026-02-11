"""Resume parsing service for extracting text from files."""
from typing import Optional
import PyPDF2
import pdfplumber
from docx import Document
import io


class ParserService:
    """Service for parsing resume files."""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_content: PDF file content as bytes
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            # Try pdfplumber first (better extraction)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            except Exception as e2:
                print(f"PyPDF2 extraction also failed: {str(e2)}")
                return ""
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_content: DOCX file content as bytes
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"DOCX extraction failed: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text(file_content: bytes, filename: str) -> Optional[str]:
        """
        Extract text from resume file based on file type.
        
        Args:
            file_content: File content as bytes
            filename: File name to determine type
            
        Returns:
            Extracted text or None if unsupported
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return ParserService.extract_text_from_pdf(file_content)
        elif filename_lower.endswith('.docx'):
            return ParserService.extract_text_from_docx(file_content)
        elif filename_lower.endswith('.txt'):
            try:
                return file_content.decode('utf-8')
            except Exception as e:
                print(f"Text file decoding failed: {str(e)}")
                return None
        else:
            print(f"Unsupported file type: {filename}")
            return None
    
    @staticmethod
    def extract_contact_info(text: str) -> dict:
        """
        Extract contact information using regex patterns.
        
        Args:
            text: Resume text
            
        Returns:
            Dict with extracted contact info
        """
        import re
        
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group(0)
        
        # Phone pattern (various formats)
        phone_pattern = r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact_info["phone"] = phone_match.group(0)
        
        # LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            contact_info["linkedin"] = f"https://{linkedin_match.group(0)}"
        
        # GitHub URL
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            contact_info["github"] = f"https://{github_match.group(0)}"
        
        return contact_info
