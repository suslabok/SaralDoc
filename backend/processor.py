"""
Text Processing Module - AI-powered document analysis
Handles Nepali and English text processing with NLP
"""

import re
import os
from typing import List, Dict, Any
import string

# Try importing NLP libraries
HAS_SPACY = False
HAS_TRANSFORMERS = False

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    pass

try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    pass

try:
    import nltk
    from nltk.tokenize import sent_tokenize
    from nltk.corpus import stopwords
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except ImportError:
    pass

# ============================================================================
# PROCESSOR CLASS
# ============================================================================

class TextProcessor:
    """Main text processing engine"""
    
    def __init__(self):
        """Initialize processor with available models"""
        self.spacy_model = None
        self.transformer = None
        self.initialize_models()
    
    def initialize_models(self):
        """Load spaCy and Transformer models"""
        if HAS_SPACY:
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
            except OSError:
                print("⚠️  spaCy model not found. Download with: python -m spacy download en_core_web_sm")
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Nepali, English, or Mixed"""
        nepali_chars = re.findall(r'[\u0900-\u097F]', text)
        english_chars = re.findall(r'[a-zA-Z]', text)
        
        nepali_ratio = len(nepali_chars) / len(text) if text else 0
        english_ratio = len(english_chars) / len(text) if text else 0
        
        if nepali_ratio > 0.5:
            return "nepali"
        elif english_ratio > 0.5:
            return "english"
        else:
            return "mixed"
    
    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Extract clauses/sentences from document"""
        # Split by sentences
        sentences = re.split(r'[।।!?]\s*', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        clauses = []
        for sentence in sentences[:50]:  # Limit to 50 clauses
            clauses.append({
                "text": sentence,
                "type": "clause",
                "confidence": 0.85
            })
        
        return clauses
    
    def extract_obligations(self, text: str) -> List[Dict[str, Any]]:
        """Extract obligations/requirements from document"""
        obligations = []
        
        # English obligation patterns
        english_patterns = [
            r'(?:shall|must|should|will|require|mandate|obligate)\s+([^.!?।।]+)',
            r'([^.!?।।]+?)\s+(?:is required|is mandatory|must be)',
            r'(?:obligation|duty|responsibility|must)\s+(?:is|to)?\s+([^.!?।।]+)',
        ]
        
        # Nepali obligation keywords
        nepali_keywords = ['गरनु पर्दछ', 'गर्नु अनिवार्य', 'आवश्यक', 'दायित्व', 'गर्नु जरुरी', 'गरिनेछ', 'गर्न सक्दैन']
        
        # English patterns
        for pattern in english_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                obligation_text = match.group(0) if match.lastindex == 0 else match.group(1)
                if obligation_text and len(obligation_text) > 5:
                    obligations.append({
                        "text": obligation_text.strip(),
                        "type": "obligation",
                        "language": "english",
                        "confidence": 0.8
                    })
        
        # Nepali patterns
        for keyword in nepali_keywords:
            matches = re.finditer(r'([^.!?।।]*' + re.escape(keyword) + r'[^.!?।।]*)', text)
            for match in matches:
                obligation_text = match.group(1).strip()
                if obligation_text and len(obligation_text) > 5:
                    obligations.append({
                        "text": obligation_text,
                        "type": "obligation",
                        "language": "nepali",
                        "confidence": 0.8
                    })
        
        # Remove duplicates
        seen = set()
        unique_obligations = []
        for obl in obligations:
            if obl["text"] not in seen:
                seen.add(obl["text"])
                unique_obligations.append(obl)
        
        return unique_obligations[:30]  # Limit to 30
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities (people, organizations, amounts, dates)"""
        entities = []
        
        # Use spaCy if available
        if self.spacy_model:
            doc = self.spacy_model(text[:1000])  # Limit text for performance
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_.lower(),
                    "confidence": 0.85
                })
        
        # Extract amounts (numbers with currency)
        amount_pattern = r'(?:Rs\.?|NPR|USD|\$|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        for match in re.finditer(amount_pattern, text):
            amount = match.group(0).strip()
            entities.append({
                "text": amount,
                "type": "amount",
                "confidence": 0.9
            })
        
        # Extract dates
        date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        for match in re.finditer(date_pattern, text):
            date = match.group(0)
            entities.append({
                "text": date,
                "type": "date",
                "confidence": 0.9
            })
        
        # Remove duplicates
        seen = set()
        unique_entities = []
        for ent in entities:
            if ent["text"] not in seen:
                seen.add(ent["text"])
                unique_entities.append(ent)
        
        return unique_entities[:20]  # Limit to 20
    
    def analyze_complexity(self, text: str) -> int:
        """Analyze document complexity (0-100)"""
        words = len(text.split())
        sentences = len(re.split(r'[।।!?]', text))
        avg_word_length = len(text.replace(" ", "")) / max(words, 1)
        
        # Score based on factors
        score = 0
        
        # Word count factor (more words = more complex)
        if words > 500:
            score += 25
        elif words > 300:
            score += 20
        elif words > 100:
            score += 10
        
        # Average word length (longer words = more complex)
        if avg_word_length > 6:
            score += 25
        elif avg_word_length > 5:
            score += 15
        
        # Sentence complexity
        if sentences > 0:
            avg_sentence_length = words / sentences
            if avg_sentence_length > 20:
                score += 25
            elif avg_sentence_length > 15:
                score += 15
        
        # Specialized vocabulary
        legal_terms = ['law', 'agreement', 'liability', 'obligation', 'clause', 'अधिनियम', 'समझौता']
        for term in legal_terms:
            if term.lower() in text.lower():
                score += 5
        
        return min(score, 100)
    
    def analyze_readability(self, text: str) -> int:
        """Analyze document readability (0-100, higher is more readable)"""
        words = len(text.split())
        sentences = len(re.split(r'[।।!?]', text))
        
        if words == 0:
            return 0
        
        # Flesch Kincaid inspired scoring
        avg_words_per_sentence = words / max(sentences, 1)
        avg_syllables = sum(self.count_syllables(word) for word in text.split()) / words
        
        # Calculate score (inverted from complexity)
        score = 100
        
        # Penalty for long sentences
        if avg_words_per_sentence > 25:
            score -= 30
        elif avg_words_per_sentence > 20:
            score -= 20
        elif avg_words_per_sentence > 15:
            score -= 10
        
        # Penalty for long words
        if avg_syllables > 3:
            score -= 20
        elif avg_syllables > 2.5:
            score -= 10
        
        return max(score, 0)
    
    def count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        syllables = 0
        vowels = "aeiououy"
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllables += 1
            previous_was_vowel = is_vowel
        
        if word.endswith("e"):
            syllables -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            syllables += 1
        
        return max(syllables, 1)
    
    def generate_summary(self, text: str) -> str:
        """Generate a brief summary of the document"""
        sentences = re.split(r'[।।!?]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            return text
        
        # Take first 1-2 sentences as summary
        summary = ' '.join(sentences[:2])
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        return summary
    
    def extract_structure(self, text: str) -> Dict[str, Any]:
        """Main processing function - extracts all information"""
        language = self.detect_language(text)
        clauses = self.extract_clauses(text)
        obligations = self.extract_obligations(text)
        entities = self.extract_entities(text)
        
        return {
            "language": language,
            "clauses": clauses,
            "obligations": obligations,
            "entities": entities,
            "text_length": len(text),
            "word_count": len(text.split()),
            "summary": self.generate_summary(text)
        }

processor = TextProcessor()

# ============================================================================
# MODULE EXPORTS
# ============================================================================

def extract_structure(text: str) -> Dict[str, Any]:
    """Public API: Extract all structure from text"""
    return processor.extract_structure(text)

def analyze_complexity(text: str) -> int:
    """Public API: Analyze complexity"""
    return processor.analyze_complexity(text)

def analyze_readability(text: str) -> int:
    """Public API: Analyze readability"""
    return processor.analyze_readability(text)

def detect_language(text: str) -> str:
    """Public API: Detect language"""
    return processor.detect_language(text)

