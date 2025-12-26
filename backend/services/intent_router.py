"""
Intent router service for domain classification
"""
import re
from typing import Dict, Any
import json

from backend.models.schemas import DomainType, IntentClassification
from backend.services.llm_client import llm_client
from backend.prompts.system_prompts import INTENT_CLASSIFICATION_PROMPT


class IntentRouter:
    """Routes user queries to appropriate domains"""
    
    def __init__(self):
        """Initialize intent router"""
        # Keywords that trigger STRICT RECRUITER persona
        self.strict_recruiter_keywords = [
            "interview", "mock interview", "technical question", "coding question",
            "resume review", "cv review", "evaluate my", "critique my",
            "test me", "quiz me", "ask me", "practice", "prepare for interview",
            "system design", "algorithm", "data structure", "solve this",
            "explain how", "implement", "code", "debug", "optimize",
            "what is the time complexity", "what is polymorphism", "what is",
            "how does", "difference between", "compare", "technical"
        ]
        
        # Keywords that trigger SUPPORTIVE MENTOR persona
        self.supportive_mentor_keywords = [
            "confused", "don't know", "not sure", "overwhelmed", "scared",
            "anxious", "worried", "what should i do", "help me decide",
            "career path", "which domain", "should i choose", "guidance",
            "lost", "stuck", "can't decide", "advice", "suggest",
            "roadmap", "plan", "how to start", "where to begin",
            "feeling", "stress", "pressure", "difficult", "hard"
        ]
        
        self.domain_keywords = {
            DomainType.SOFTWARE_DEV: [
                "code", "coding", "programming", "web", "app", "software", "developer",
                "javascript", "python", "java", "react", "node", "backend", "frontend",
                "fullstack", "database", "sql", "api", "git", "algorithm", "dsa",
                "leetcode", "system design", "cloud", "aws", "docker", "devops"
            ],
            DomainType.AI_ML: [
                "machine learning", "ml", "ai", "artificial intelligence", "neural network",
                "deep learning", "data science", "tensorflow", "pytorch", "model",
                "nlp", "computer vision", "cnn", "rnn", "transformer", "generative",
                "dataset", "training", "inference", "feature engineering", "mlops"
            ],
            DomainType.VLSI: [
                "vlsi", "chip", "ic design", "rtl", "verilog", "vhdl", "asic", "fpga",
                "analog", "digital", "layout", "synthesis", "verification", "timing",
                "semiconductor", "cadence", "synopsys", "eda", "physical design"
            ],
            DomainType.EMBEDDED: [
                "embedded", "microcontroller", "mcu", "firmware", "iot", "arduino",
                "raspberry pi", "arm", "rtos", "uart", "spi", "i2c", "can", "sensor",
                "actuator", "driver", "hardware", "low level", "bare metal"
            ],
            DomainType.MECHANICAL: [
                "mechanical", "cad", "cam", "solidworks", "autocad", "catia", "ansys",
                "manufacturing", "design", "thermodynamics", "fluid", "heat transfer",
                "fea", "cfd", "automation", "robotics", "product design", "quality"
            ],
            DomainType.SOFT_SKILLS: [
                "communication", "leadership", "teamwork", "soft skill", "presentation",
                "interview skill", "confidence", "body language", "email", "networking",
                "emotional intelligence", "conflict", "time management", "organization",
                "problem solving", "critical thinking", "behavioral interview"
            ]
        }
    
    async def classify_intent(self, query: str, use_llm: bool = True) -> IntentClassification:
        """
        Classify user query into domain, intent, and persona
        
        Args:
            query: User's query
            use_llm: Whether to use LLM for classification (fallback to keyword matching)
        
        Returns:
            Intent classification result with persona
        """
        # Try keyword-based classification first
        keyword_result = self._classify_by_keywords(query)
        
        # Detect persona
        persona = self._detect_persona(query)
        keyword_result["persona"] = persona
        
        if keyword_result["confidence"] > 0.7 or not use_llm:
            return IntentClassification(**keyword_result)
        
        # Use LLM for more accurate classification
        try:
            llm_result = await self._classify_by_llm(query)
            llm_result["persona"] = persona  # Override with detected persona
            return IntentClassification(**llm_result)
        except Exception as e:
            # Fallback to keyword classification
            print(f"LLM classification failed: {e}")
            return IntentClassification(**keyword_result)
    
    def _classify_by_keywords(self, query: str) -> Dict[str, Any]:
        """
        Classify query using keyword matching
        
        Args:
            query: User's query
        
        Returns:
            Classification result
        """
        query_lower = query.lower()
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in query_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                domain_scores[domain] = {
                    "score": score,
                    "keywords": matched_keywords
                }
        
        if not domain_scores:
            return {
                "domain": DomainType.GENERAL,
                "confidence": 0.5,
                "intent": "general_query",
                "entities": {}
            }
        
        # Get domain with highest score
        best_domain = max(domain_scores.items(), key=lambda x: x[1]["score"])
        domain = best_domain[0]
        score = best_domain[1]["score"]
        keywords = best_domain[1]["keywords"]
        
        # Normalize confidence score
        confidence = min(score / 3, 0.95)  # Cap at 0.95
        
        # Extract basic intent
        intent = self._extract_basic_intent(query_lower)
        
        return {
            "domain": domain,
            "confidence": confidence,
            "intent": intent,
            "entities": {"matched_keywords": keywords}
        }
    
    def _detect_persona(self, query: str) -> str:
        """Detect which persona to use based on query"""
        query_lower = query.lower()
        
        # Check for strict recruiter triggers
        strict_score = sum(1 for keyword in self.strict_recruiter_keywords if keyword in query_lower)
        
        # Check for supportive mentor triggers
        supportive_score = sum(1 for keyword in self.supportive_mentor_keywords if keyword in query_lower)
        
        # Check for question patterns that indicate technical assessment
        technical_patterns = [r"what is", r"explain", r"how does", r"difference between", 
                            r"implement", r"solve", r"write code", r"time complexity"]
        has_technical_pattern = any(re.search(pattern, query_lower) for pattern in technical_patterns)
        
        # Determine persona
        if strict_score > supportive_score or has_technical_pattern:
            return "strict_recruiter"
        elif supportive_score > 0:
            return "supportive_mentor"
        else:
            # Default to supportive mentor for ambiguous queries
            return "supportive_mentor"
    
    def _extract_basic_intent(self, query: str) -> str:
        """Extract basic intent from query"""
        intent_patterns = {
            "resume_review": r"(resume|cv|curriculum vitae)",
            "interview_prep": r"(interview|mock interview|practice)",
            "skill_assessment": r"(skill|learn|improve|gap)",
            "company_research": r"(company|organization|firm)",
            "project_suggestion": r"(project|build|create|develop)",
            "career_advice": r"(career|path|guidance|advice)",
            "job_search": r"(job|position|opening|opportunity)"
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, query):
                return intent
        
        return "general_query"
    
    async def _classify_by_llm(self, query: str) -> Dict[str, Any]:
        """
        Classify query using LLM
        
        Args:
            query: User's query
        
        Returns:
            Classification result
        """
        prompt = INTENT_CLASSIFICATION_PROMPT.format(query=query)
        
        response = await llm_client.generate_with_json_response(
            prompt=prompt,
            system_prompt="You are an expert at classifying student queries for placement preparation."
        )
        
        # Validate and normalize response
        domain_str = response.get("domain", "general")
        
        # Map string to DomainType enum
        domain_mapping = {
            "software_development": DomainType.SOFTWARE_DEV,
            "ai_ml": DomainType.AI_ML,
            "vlsi": DomainType.VLSI,
            "embedded": DomainType.EMBEDDED,
            "mechanical": DomainType.MECHANICAL,
            "soft_skills": DomainType.SOFT_SKILLS,
            "general": DomainType.GENERAL
        }
        
        domain = domain_mapping.get(domain_str, DomainType.GENERAL)
        
        return {
            "domain": domain,
            "confidence": float(response.get("confidence", 0.8)),
            "intent": response.get("intent", "general_query"),
            "entities": response.get("entities", {})
        }
    
    def get_domain_context(self, domain: DomainType) -> str:
        """
        Get contextual information about a domain
        
        Args:
            domain: Domain type
        
        Returns:
            Domain context description
        """
        context_map = {
            DomainType.SOFTWARE_DEV: "Software Development and Programming",
            DomainType.AI_ML: "Artificial Intelligence and Machine Learning",
            DomainType.VLSI: "VLSI and Chip Design",
            DomainType.EMBEDDED: "Embedded Systems and Firmware",
            DomainType.MECHANICAL: "Mechanical Engineering",
            DomainType.SOFT_SKILLS: "Soft Skills and Professional Development",
            DomainType.GENERAL: "General Placement Guidance"
        }
        
        return context_map.get(domain, "General Guidance")


# Singleton instance
intent_router = IntentRouter()
