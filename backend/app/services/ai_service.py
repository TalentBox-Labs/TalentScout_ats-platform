"""AI service for resume parsing, matching, and screening."""
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from app.config import settings

# Initialize AsyncOpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)


class AIService:
    """Service for AI-powered features."""
    
    @staticmethod
    async def parse_resume_text(resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text using GPT-4 to extract structured data.
        
        Args:
            resume_text: Raw text extracted from resume
            
        Returns:
            Structured resume data
        """
        prompt = f"""
        Extract structured information from the following resume. Return a JSON object with this structure:
        {{
            "contact": {{"email": "", "phone": "", "location": "", "linkedin": "", "github": ""}},
            "summary": "Brief professional summary",
            "experience": [
                {{
                    "company": "",
                    "title": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "is_current": false,
                    "description": ""
                }}
            ],
            "education": [
                {{
                    "institution": "",
                    "degree": "",
                    "field_of_study": "",
                    "start_date": "",
                    "end_date": "",
                    "grade": ""
                }}
            ],
            "skills": ["skill1", "skill2", ...],
            "certifications": ["cert1", "cert2", ...],
            "total_experience_years": 0
        }}
        
        Resume:
        {resume_text}
        """
        
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert resume parser. Extract structured data from resumes accurately."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            
            import json
            parsed_data = json.loads(response.choices[0].message.content)
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing resume: {str(e)}")
            return {}
    
    @staticmethod
    async def generate_candidate_summary(candidate_data: Dict[str, Any]) -> str:
        """
        Generate an AI summary of a candidate's profile.
        
        Args:
            candidate_data: Candidate profile data
            
        Returns:
            AI-generated summary
        """
        prompt = f"""
        Create a concise 2-3 sentence professional summary for this candidate:
        
        Name: {candidate_data.get('full_name', 'Candidate')}
        Experience: {candidate_data.get('total_experience_years', 0)} years
        Skills: {', '.join(candidate_data.get('skills', [])[:10])}
        Recent Role: {candidate_data.get('headline', 'N/A')}
        
        Focus on their expertise and value proposition.
        """
        
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter writing candidate summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return ""
    
    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = await client.embeddings.create(
                model=settings.openai_embedding_model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return []
    
    @staticmethod
    async def screen_candidate(
        candidate_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        AI screening of candidate against job requirements.
        
        Args:
            candidate_data: Candidate profile data
            job_data: Job requirements data
            
        Returns:
            Screening results with score and insights
        """
        # Format candidate profile
        candidate_profile = f"""
        Name: {candidate_data.get('name', 'N/A')}
        Email: {candidate_data.get('email', 'N/A')}
        Current Position: {candidate_data.get('current_position', 'N/A')}
        Current Company: {candidate_data.get('current_company', 'N/A')}
        Years of Experience: {candidate_data.get('years_of_experience', 'N/A')}
        Location: {candidate_data.get('location', 'N/A')}
        Summary: {candidate_data.get('summary', 'N/A')}
        """
        
        # Format job requirements
        job_requirements = f"""
        Title: {job_data.get('title', 'N/A')}
        Description: {job_data.get('description', 'N/A')}
        Requirements: {job_data.get('requirements', 'N/A')}
        Responsibilities: {job_data.get('responsibilities', 'N/A')}
        Skills Required: {', '.join(job_data.get('skills_required', []))}
        Experience Level: {job_data.get('experience_level', 'N/A')}
        Location: {job_data.get('location', 'N/A')}
        """
        
        prompt = f"""
        Evaluate this candidate against the job requirements. Provide a structured assessment.
        
        JOB REQUIREMENTS:
        {job_requirements}
        
        CANDIDATE PROFILE:
        {candidate_profile}
        
        Return a JSON object with:
        {{
            "fit_score": 0-100,
            "recommendation": "strong_fit" | "maybe" | "not_fit",
            "strengths": ["strength1", "strength2", ...],
            "concerns": ["concern1", "concern2", ...],
            "summary": "Brief assessment summary",
            "suggested_questions": ["question1", "question2", ...]
        }}
        """
        
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert technical recruiter evaluating candidate fit."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            
            import json
            screening_result = json.loads(response.choices[0].message.content)
            return screening_result
            
        except Exception as e:
            print(f"Error screening candidate: {str(e)}")
            return {}
    
    @staticmethod
    async def generate_email(
        context: Dict[str, Any],
        email_type: str,
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate personalized email content.
        
        Args:
            context: Context data (candidate name, job title, etc.)
            email_type: Type of email (rejection, interview_invite, offer, etc.)
            tone: Email tone (professional, friendly, casual)
            
        Returns:
            Dict with subject and body
        """
        email_templates = {
            "rejection": "Write a respectful rejection email",
            "interview_invite": "Write an interview invitation email",
            "offer": "Write a job offer email",
            "follow_up": "Write a follow-up email to check on application status",
        }
        
        instruction = email_templates.get(email_type, "Write a professional email")
        
        prompt = f"""
        {instruction} with a {tone} tone.
        
        Context:
        - Candidate Name: {context.get('candidate_name', 'Candidate')}
        - Job Title: {context.get('job_title', 'Position')}
        - Company: {context.get('company_name', 'Our Company')}
        {f"- Additional: {context.get('additional_info', '')}" if context.get('additional_info') else ""}
        
        Return JSON:
        {{
            "subject": "Email subject line",
            "body": "Email body in HTML format"
        }}
        """
        
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional recruiter writing candidate emails."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            
            import json
            email_content = json.loads(response.choices[0].message.content)
            return email_content
            
        except Exception as e:
            print(f"Error generating email: {str(e)}")
            return {"subject": "", "body": ""}
    
    @staticmethod
    async def generate_job_description(
        title: str,
        department: Optional[str] = None,
        experience_level: Optional[str] = None,
        key_skills: Optional[List[str]] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive job description using AI.
        
        Args:
            title: Job title
            department: Department (optional)
            experience_level: Experience level (optional)
            key_skills: Key skills required (optional)
            additional_context: Additional context (optional)
            
        Returns:
            Dict with title, description, requirements, responsibilities, suggested_skills
        """
        skills_text = ", ".join(key_skills) if key_skills else "relevant skills for the role"
        
        prompt = f"""
        Generate a comprehensive job description for the following role:
        
        Title: {title}
        Department: {department or 'Not specified'}
        Experience Level: {experience_level or 'Not specified'}
        Key Skills: {skills_text}
        {f"Additional Context: {additional_context}" if additional_context else ""}
        
        Return a JSON object with:
        {{
            "title": "Full job title",
            "description": "Detailed job description (3-4 paragraphs)",
            "requirements": "Key requirements and qualifications",
            "responsibilities": "Main responsibilities and duties",
            "suggested_skills": ["skill1", "skill2", "skill3", ...]
        }}
        """
        
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert HR professional writing job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
            )
            
            import json
            job_desc = json.loads(response.choices[0].message.content)
            return job_desc
            
        except Exception as e:
            print(f"Error generating job description: {str(e)}")
            return {
                "title": title,
                "description": "",
                "requirements": "",
                "responsibilities": "",
                "suggested_skills": key_skills or []
            }
    
    @staticmethod
    async def generate_interview_questions(
        job_context: Dict[str, Any],
        question_types: Optional[List[str]] = None,
        count: int = 5
    ) -> List[str]:
        """
        Generate interview questions based on job context.
        
        Args:
            job_context: Job details (title, description, requirements, etc.)
            question_types: Types of questions to generate (optional)
            count: Number of questions to generate
            
        Returns:
            List of interview questions
        """
        # Format job context
        job_description = f"""
        Title: {job_context.get('title', 'N/A')}
        Description: {job_context.get('description', 'N/A')}
        Requirements: {job_context.get('requirements', 'N/A')}
        Experience Level: {job_context.get('experience_level', 'N/A')}
        """
        
        # Include question types if specified
        type_instruction = ""
        if question_types:
            type_instruction = f"Focus on these types of questions: {', '.join(question_types)}. "
        
        prompt = f"""
        Generate {count} insightful interview questions for this role.
        {type_instruction}
        
        {job_description}
        
        Focus on assessing key skills, experience, and cultural fit.
        Return as a JSON array of strings.
        """
        
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You are an experienced hiring manager creating interview questions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("questions", [])
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return []

    @staticmethod
    async def enhance_email(body: str) -> Dict[str, str]:
        """
        Light-weight compatibility helper used by communications router.
        Returns original body if enhancement fails or AI is unavailable.
        """
        if not body:
            return {"body": ""}

        prompt = f"""
        Improve the following email for clarity and professionalism while preserving intent.
        Return JSON with one field: {{"body": "enhanced html body"}}.

        Email:
        {body}
        """
        try:
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "You improve recruiting emails."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            import json

            parsed = json.loads(response.choices[0].message.content)
            return {"body": parsed.get("body", body)}
        except Exception:
            return {"body": body}
