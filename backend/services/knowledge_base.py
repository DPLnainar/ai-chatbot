"""
Knowledge base service with simple in-memory storage
"""
import os
from typing import List, Optional, Dict, Any
import json

from backend.config import config
from backend.models.schemas import KnowledgeDocument


class KnowledgeBase:
    """Manages knowledge base and retrieval"""
    
    def __init__(self):
        """Initialize knowledge base with in-memory storage"""
        self.documents = []  # Simple in-memory storage
        os.makedirs(os.path.dirname(config.VECTOR_DB_PATH) if config.VECTOR_DB_PATH else "./data", exist_ok=True)
    
    def add_document(
        self,
        content: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add document to knowledge base
        
        Args:
            content: Document content
            source: Source identifier
            metadata: Optional metadata
            doc_id: Optional document ID
        
        Returns:
            Document ID
        """
        if not doc_id:
            doc_id = f"{source}_{hash(content)}"
        
        full_metadata = {"source": source}
        if metadata:
            full_metadata.update(metadata)
        
        doc = {
            "id": doc_id,
            "content": content,
            "source": source,
            "metadata": full_metadata
        }
        
        self.documents.append(doc)
        return doc_id
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple documents in batch
        
        Args:
            documents: List of document dicts with 'content', 'source', 'metadata', 'doc_id'
        
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for doc in documents:
            content = doc["content"]
            source = doc["source"]
            metadata = doc.get("metadata", {})
            doc_id = doc.get("doc_id", f"{source}_{hash(content)}")
            
            full_metadata = {"source": source}
            full_metadata.update(metadata)
            
            self.documents.append({
                "id": doc_id,
                "content": content,
                "source": source,
                "metadata": full_metadata
            })
            
            doc_ids.append(doc_id)
        
        return doc_ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[KnowledgeDocument]:
        """
        Search knowledge base for relevant documents using simple keyword matching
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant documents
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        
        for doc in self.documents:
            # Apply metadata filter if provided
            if filter_metadata:
                match = True
                for key, value in filter_metadata.items():
                    if doc["metadata"].get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            # Simple keyword matching for relevance
            content_lower = doc["content"].lower()
            content_words = set(content_lower.split())
            
            # Calculate overlap score
            overlap = len(query_words & content_words)
            if overlap > 0 or any(word in content_lower for word in query_words):
                score = overlap + sum(1 for word in query_words if word in content_lower)
                results.append((doc, score))
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to KnowledgeDocument objects
        documents = []
        for doc, score in results[:top_k]:
            documents.append(KnowledgeDocument(
                content=doc["content"],
                source=doc["source"],
                metadata=doc["metadata"],
                relevance_score=score / 10.0  # Normalize score
            ))
        
        return documents
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from knowledge base
        
        Args:
            doc_id: Document ID
        
        Returns:
            Success status
        """
        try:
            self.documents = [doc for doc in self.documents if doc["id"] != doc_id]
            return True
        except Exception:
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "total_documents": len(self.documents),
            "collection_name": "placement_knowledge"
        }
    
    def load_default_knowledge(self):
        """Load default placement knowledge into the database"""
        default_docs = [
            {
                "content": "Resume tips: Keep it to 1-2 pages. Use action verbs. Quantify achievements. Include relevant projects. Tailor to each job. Proofread carefully.",
                "source": "resume_guide",
                "metadata": {"category": "resume", "domain": "general"}
            },
            {
                "content": "Common interview questions for software developers: Tell me about yourself, explain your projects, coding challenges, system design, behavioral questions about teamwork and problem-solving.",
                "source": "interview_guide",
                "metadata": {"category": "interview", "domain": "software_development"}
            },
            {
                "content": "Data Structures to master: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables, Heaps. Practice on LeetCode, HackerRank, CodeForces.",
                "source": "dsa_guide",
                "metadata": {"category": "technical_skills", "domain": "software_development"}
            },
            {
                "content": "AI/ML interview preparation: Know ML algorithms, understand bias-variance tradeoff, explain model evaluation metrics, discuss real projects, understand MLOps and deployment.",
                "source": "aiml_guide",
                "metadata": {"category": "interview", "domain": "ai_ml"}
            },
            {
                "content": "VLSI interview topics: RTL design flow, synthesis, verification methodologies, timing analysis, low-power design techniques, EDA tools experience.",
                "source": "vlsi_guide",
                "metadata": {"category": "interview", "domain": "vlsi"}
            },
            {
                "content": "Embedded systems skills: C/C++ programming, microcontroller architecture, RTOS concepts, communication protocols (UART, SPI, I2C), hardware debugging.",
                "source": "embedded_guide",
                "metadata": {"category": "technical_skills", "domain": "embedded"}
            },
            {
                "content": "Mechanical engineering interviews: CAD modeling skills, manufacturing processes, material science, thermodynamics concepts, real project experience with FEA/CFD.",
                "source": "mechanical_guide",
                "metadata": {"category": "interview", "domain": "mechanical"}
            },
            {
                "content": "Soft skills for placements: Communication clarity, active listening, teamwork, leadership examples, time management, adaptability, problem-solving approach.",
                "source": "softskills_guide",
                "metadata": {"category": "soft_skills", "domain": "soft_skills"}
            },
            {
                "content": "Top tech companies for software roles: Google, Microsoft, Amazon, Apple, Meta, Netflix, Adobe, Salesforce. Prepare for their specific interview patterns.",
                "source": "companies_guide",
                "metadata": {"category": "companies", "domain": "software_development"}
            },
            {
                "content": "Salary negotiation tips: Research market rates, highlight your value, be confident but realistic, consider total compensation, don't accept the first offer immediately.",
                "source": "negotiation_guide",
                "metadata": {"category": "career_advice", "domain": "general"}
            }
        ]
        
        try:
            self.add_documents_batch(default_docs)
            print(f"Loaded {len(default_docs)} default documents into knowledge base")
        except Exception as e:
            print(f"Error loading default knowledge: {e}")


# Singleton instance
knowledge_base = KnowledgeBase()


# Initialize default knowledge on first import
try:
    if knowledge_base.get_collection_stats()["total_documents"] == 0:
        knowledge_base.load_default_knowledge()
except Exception as e:
    print(f"Warning: Could not initialize default knowledge: {e}")
