from typing import List, Dict, Tuple
from collections import defaultdict, Counter
import json
from datetime import datetime
from pathlib import Path

class DocumentAnalytics:
    """Advanced analytics for processed documents"""
    
    def __init__(self):
        self.analysis_history = []
        self.document_stats = defaultdict(int)
    
    def analyze_document_complexity(self, document: Dict) -> Dict:
        """Calculate document complexity score"""
        clauses = document.get('clauses', [])
        obligations = document.get('obligations', [])
        entities = document.get('entities', {})
        
        # Complexity factors
        clause_complexity = min(len(clauses) / 20, 1.0)  # Normalized to 0-1
        obligation_complexity = min(len(obligations) / 15, 1.0)
        entity_complexity = sum(min(len(v) / 10, 1.0) for v in entities.values()) / len(entities) if entities else 0
        
        # Calculate overall complexity (0-100 scale)
        complexity_score = ((clause_complexity + obligation_complexity + entity_complexity) / 3) * 100
        
        return {
            "overall_score": round(complexity_score, 2),
            "factors": {
                "clauses": clause_complexity,
                "obligations": obligation_complexity,
                "entities": entity_complexity
            },
            "level": self._get_complexity_level(complexity_score)
        }
    
    @staticmethod
    def _get_complexity_level(score: float) -> str:
        """Get complexity level based on score"""
        if score < 30:
            return "Simple"
        elif score < 60:
            return "Moderate"
        elif score < 80:
            return "Complex"
        else:
            return "Very Complex"
    
    def identify_risk_areas(self, document: Dict) -> List[Dict]:
        """Identify high-risk areas in document"""
        risks = []
        obligations = document.get('obligations', [])
        
        # Check for high-risk obligation types
        high_risk_keywords = [
            "liability", "indemnify", "breach", "penalty", "damages",
            "दण्ड", "जरिवाना", "क्षति", "दायित्व"
        ]
        
        for obligation in obligations:
            clause = obligation.get('clause', '').lower()
            obl_type = obligation.get('type', '').lower()
            
            # Check for risk keywords
            for keyword in high_risk_keywords:
                if keyword.lower() in clause or keyword.lower() in obl_type:
                    risks.append({
                        "risk_type": "High-risk obligation",
                        "clause_excerpt": obligation.get('clause', '')[:100],
                        "severity": "high",
                        "recommendation": "Review carefully before signing"
                    })
                    break
            
            # Check for undefined terms
            if len(clause) > 200:
                risks.append({
                    "risk_type": "Complex clause",
                    "clause_excerpt": clause[:100],
                    "severity": "medium",
                    "recommendation": "Ensure full understanding of implications"
                })
        
        return risks
    
    def compare_documents(self, doc1: Dict, doc2: Dict) -> Dict:
        """Compare two documents"""
        comparison = {
            "document_1": {
                "clauses": len(doc1.get('clauses', [])),
                "obligations": len(doc1.get('obligations', [])),
                "language": doc1.get('language', 'unknown')
            },
            "document_2": {
                "clauses": len(doc2.get('clauses', [])),
                "obligations": len(doc2.get('obligations', [])),
                "language": doc2.get('language', 'unknown')
            },
            "differences": {
                "clause_difference": len(doc1.get('clauses', [])) - len(doc2.get('clauses', [])),
                "obligation_difference": len(doc1.get('obligations', [])) - len(doc2.get('obligations', []))
            }
        }
        
        return comparison
    
    def generate_summary_statistics(self, documents: List[Dict]) -> Dict:
        """Generate statistics for multiple documents"""
        if not documents:
            return {}
        
        total_clauses = sum(len(doc.get('clauses', [])) for doc in documents)
        total_obligations = sum(len(doc.get('obligations', [])) for doc in documents)
        
        languages = [doc.get('language', 'unknown') for doc in documents]
        language_distribution = Counter(languages)
        
        avg_complexity = sum(
            self.analyze_document_complexity(doc)['overall_score'] 
            for doc in documents
        ) / len(documents)
        
        return {
            "total_documents": len(documents),
            "total_clauses": total_clauses,
            "total_obligations": total_obligations,
            "average_clauses_per_document": round(total_clauses / len(documents), 2),
            "average_obligations_per_document": round(total_obligations / len(documents), 2),
            "language_distribution": dict(language_distribution),
            "average_complexity": round(avg_complexity, 2)
        }
    
    def extract_key_terms(self, document: Dict, top_n: int = 10) -> List[str]:
        """Extract key terms from document"""
        clauses = document.get('clauses', [])
        obligations = document.get('obligations', [])
        
        # Combine all text
        all_text = ' '.join(clauses) + ' '.join(obl['clause'] for obl in obligations)
        
        # Simple keyword extraction
        words = all_text.split()
        
        # Filter out common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'as', 'is', 'be', 'by', 'this', 'that', 'है', 'को', 'में',
            'यो', 'ले', 'लाई', 'वा', 'र'
        }
        
        key_words = [w for w in words if w.lower() not in stop_words and len(w) > 3]
        word_freq = Counter(key_words)
        
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def calculate_readability_score(self, text: str) -> Dict:
        """Calculate document readability"""
        sentences = text.split('.')
        words = text.split()
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Simple readability score (Flesch-Kincaid approximation)
        readability = 100 - (avg_sentence_length * 5)
        readability = max(0, min(100, readability))  # Clamp to 0-100
        
        return {
            "score": round(readability, 2),
            "level": self._get_readability_level(readability),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(len(text) / len(words), 2) if words else 0
        }
    
    @staticmethod
    def _get_readability_level(score: float) -> str:
        """Get readability level"""
        if score > 80:
            return "Very Easy"
        elif score > 60:
            return "Easy"
        elif score > 40:
            return "Moderate"
        elif score > 20:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def generate_audit_trail(self, analysis_result: Dict) -> Dict:
        """Generate audit trail for document analysis"""
        return {
            "timestamp": datetime.now().isoformat(),
            "document_type": analysis_result.get('language'),
            "num_clauses": len(analysis_result.get('clauses', [])),
            "num_obligations": len(analysis_result.get('obligations', [])),
            "confidence": analysis_result.get('confidence', 0),
            "processing_time": analysis_result.get('processing_time', 0)
        }
    
    def export_analysis_report(self, analysis: Dict, 
                              output_file: str = "analysis_report.json") -> str:
        """Export analysis as JSON report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "document_analysis": analysis,
            "complexity": self.analyze_document_complexity(analysis),
            "risks": self.identify_risk_areas(analysis),
            "key_terms": self.extract_key_terms(analysis),
            "readability": self.calculate_readability_score(
                ' '.join(analysis.get('clauses', []))
            )
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(output_path)

# Global analytics instance
analytics = DocumentAnalytics()
