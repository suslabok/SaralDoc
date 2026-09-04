"""
Text Processing Module - AI-powered document analysis
Handles Nepali and English text processing with NLP.

Phase 2 upgrade notes
----------------------
Previously "AI" here meant regex + hardcoded keyword lists. This version adds:
  - Real extractive summarization via TextRank (TF-IDF sentence graph + PageRank)
  - Clause TYPE classification (obligation/payment/termination/etc.) via TF-IDF
    cosine similarity against seed examples, instead of every sentence being
    labeled generically "clause"
  - Properly wired spaCy NER (was imported but silently unused before)
  - An optional multilingual transformer NER pipeline for Nepali entities,
    lazily loaded so a machine without internet/GPU still works fine in
    regex+TF-IDF-only mode (everything above needs no external model download)

Everything degrades gracefully: if a heavier model isn't available, the
pipeline falls back to the next tier down rather than crashing.
"""

import re
import os
from typing import List, Dict, Any, Tuple
import string

HAS_SPACY = False
HAS_TRANSFORMERS = False
HAS_SKLEARN = False
HAS_NETWORKX = False

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
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    pass

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    joblib = None

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    pass

_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
_TRAINED_CLASSIFIER_PATH = os.path.join(_MODEL_DIR, "clause_classifier.joblib")

CLAUSE_CATEGORIES: Dict[str, List[str]] = {
    "governing_law": [
        "This agreement shall be governed by and construed in accordance with the laws of Nepal.",
        "Any dispute arising from this contract shall be subject to the exclusive jurisdiction of Nepali courts.",
        "This contract shall be interpreted under the applicable law of the country.",
        "This agreement shall be governed by, and construed in accordance with, the laws of the State of New York.",
    ],
    "termination": [
        "This agreement may be terminated by either party with thirty days written notice.",
        "Either party may terminate this agreement for convenience upon sixty days prior written notice.",
        "This agreement shall continue in force for a term of twelve months from the effective date, unless terminated earlier.",
        "The contract shall automatically terminate upon completion of the project.",
    ],
    "penalty": [
        "Failure to comply with this clause will result in a penalty equal to ten percent of contract value.",
        "Any breach of this agreement shall attract a fine as determined under applicable law.",
        "Late delivery shall be subject to liquidated damages.",
        "In the event of a material breach, the breaching party shall pay liquidated damages as specified herein.",
    ],
    "license_grant": [
        "Subject to the terms of this Agreement, Licensor hereby grants to Licensee a non-exclusive license to use the Licensed Technology.",
        "Each party grants to the other a non-exclusive right and license to use the intellectual property described herein.",
        "The Company hereby grants to Customer a limited, non-transferable license to use the Software.",
    ],
    "liability_cap": [
        "Neither party's aggregate liability under this Agreement shall exceed the total fees paid in the preceding twelve months.",
        "Each party's total liability arising out of this Agreement shall not exceed the amount paid under this Agreement.",
        "In no event shall either party be liable for any indirect, incidental, or consequential damages.",
    ],
    "insurance": [
        "Each party shall maintain commercial general liability insurance with coverage of at least one million dollars.",
        "The Contractor shall maintain insurance policies as required under this Agreement throughout the term.",
        "Each policy will include a provision requiring notice to the other party prior to any cancellation or non-renewal.",
    ],
    "non_compete": [
        "During the term of this Agreement and for two years thereafter, the Contractor shall not engage in any competing business.",
        "Neither party shall, directly or indirectly, solicit or compete with the other party's business during the term hereof.",
        "The Distributor will not market or sell competing products during the term of this Agreement.",
    ],
    "audit_rights": [
        "Upon reasonable written notice, the auditing Party shall have the right to audit the books and records of the other Party.",
        "Either party may, no more than once per year, inspect and audit the relevant records of the other party.",
        "The Company shall have the right to audit Licensee's compliance with this Agreement during normal business hours.",
    ],
    # Nepali seed examples for the cosine-similarity fallback path (used
    # when no trained model is present). The trained model normally covers
    # Nepali via datasets/nepali_clause_dataset.csv + trainer.py instead;
    # these exist so the untrained fallback isn't purely English-only.
    "governing_law_ne": [
        "यो सम्झौता नेपालको प्रचलित कानून बमोजिम व्याख्या तथा कार्यान्वयन गरिनेछ।",
        "यस करारसँग सम्बन्धित कुनै पनि विवाद नेपाल सरकारको अदालतको अधिकार क्षेत्रमा पर्नेछ।",
    ],
    "termination_ne": [
        "कुनै पनि पक्षले तीस दिनको पूर्व लिखित सूचना दिई यो सम्झौता समाप्त गर्न सक्नेछ।",
        "यो करार दुई वर्षको अवधिको लागि प्रभावकारी रहनेछ र सो अवधि पछि स्वतः समाप्त हुनेछ।",
    ],
    "penalty_ne": [
        "यस सम्झौताको कुनै शर्त उल्लङ्घन गरेमा उल्लङ्घन गर्ने पक्षले करार रकमको दस प्रतिशत हर्जाना तिर्नुपर्नेछ।",
        "निर्धारित समयभित्र काम सम्पन्न नगरेमा प्रति दिन कुल रकमको ०.५ प्रतिशतका दरले विलम्ब शुल्क लाग्नेछ।",
    ],
}

# Map the "_ne" suffixed keys back onto their real category when building
# the fallback similarity index, so "governing_law_ne" examples still count
# as "governing_law" for classification purposes.
for _key in list(CLAUSE_CATEGORIES.keys()):
    if _key.endswith("_ne"):
        _base = _key[: -len("_ne")]
        CLAUSE_CATEGORIES.setdefault(_base, [])
        CLAUSE_CATEGORIES[_base].extend(CLAUSE_CATEGORIES.pop(_key))

_STOPWORD_SAFE_TOKEN_PATTERN = r"(?u)\b[\w\u0900-\u097F]+\b"


class ClauseClassifier:
    """
    Clause type classifier. Prefers a trained TF-IDF + Logistic Regression
    model (models/clause_classifier.joblib, produced by trainer.py) if one
    exists. Falls back to TF-IDF cosine similarity against hand-written
    seed examples if no trained model is present — e.g. a fresh checkout
    where `python trainer.py` hasn't been run yet. Either way this needs no
    external model download and works identically for English and Nepali.
    """

    CONFIDENCE_FLOOR = 0.08  # below this, label as "general" rather than guess

    def __init__(self):
        self.trained_model = None
        self.using_trained_model = False

        if HAS_JOBLIB and os.path.exists(_TRAINED_CLASSIFIER_PATH):
            try:
                self.trained_model = joblib.load(_TRAINED_CLASSIFIER_PATH)
                self.using_trained_model = True
            except Exception as e:
                print(f"Could not load trained clause classifier, falling back to seed similarity: {e}")

        self.available = HAS_SKLEARN
        if not self.available:
            return

        self.labels: List[str] = []
        self.seed_texts: List[str] = []
        for category, examples in CLAUSE_CATEGORIES.items():
            for ex in examples:
                self.labels.append(category)
                self.seed_texts.append(ex)

        self.vectorizer = TfidfVectorizer(
            token_pattern=_STOPWORD_SAFE_TOKEN_PATTERN,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )
        self._seed_matrix = self.vectorizer.fit_transform(self.seed_texts)

    def classify(self, sentence: str) -> Tuple[str, float]:
        """Return (best_category, confidence 0-1). Falls back to 'general'."""
        if not sentence.strip():
            return "general", 0.0

        if self.using_trained_model:
            try:
                proba = self.trained_model.predict_proba([sentence])[0]
                classes = self.trained_model.classes_
                best_idx = int(np.argmax(proba)) if HAS_SKLEARN else max(range(len(proba)), key=lambda i: proba[i])
                return classes[best_idx], round(float(proba[best_idx]), 3)
            except Exception:
                pass  # fall through to seed-similarity approach

        if not self.available:
            return "general", 0.0

        vec = self.vectorizer.transform([sentence])
        sims = cosine_similarity(vec, self._seed_matrix)[0]
        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])

        if best_score < self.CONFIDENCE_FLOOR:
            return "general", round(best_score, 3)

        return self.labels[best_idx], round(min(best_score * 1.6, 0.98), 3)


class TextRankSummarizer:
    """
    Extractive summarizer: builds a sentence-similarity graph (TF-IDF cosine)
    and ranks sentences with PageRank, then returns the top-N sentences in
    their original order. Standard TextRank approach — no model download,
    works for English and Nepali alike.
    """

    def __init__(self):
        self.available = HAS_SKLEARN and HAS_NETWORKX

    def summarize(self, sentences: List[str], top_n: int = 3, max_chars: int = 400) -> str:
        clean = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]

        if not clean:
            return ""
        if len(clean) <= top_n:
            summary = " ".join(clean)
            return summary if len(summary) <= max_chars else summary[: max_chars - 3] + "..."

        if not self.available:
            summary = " ".join(clean[:top_n])
            return summary if len(summary) <= max_chars else summary[: max_chars - 3] + "..."

        try:
            vectorizer = TfidfVectorizer(token_pattern=_STOPWORD_SAFE_TOKEN_PATTERN)
            matrix = vectorizer.fit_transform(clean)
            sim_matrix = cosine_similarity(matrix)

            graph = nx.from_numpy_array(sim_matrix)
            scores = nx.pagerank(graph, max_iter=200)

            ranked_idx = sorted(scores, key=scores.get, reverse=True)[:top_n]
            ranked_idx.sort()  # restore original reading order

            summary = " ".join(clean[i] for i in ranked_idx)
            return summary if len(summary) <= max_chars else summary[: max_chars - 3] + "..."
        except Exception:
            summary = " ".join(clean[:top_n])
            return summary if len(summary) <= max_chars else summary[: max_chars - 3] + "..."

class TextProcessor:
    """Main text processing engine"""

    # Multilingual NER model: covers Nepali + English + many other languages.
    # Downloaded lazily on first use of Nepali/mixed-text entity extraction —
    # NOT at startup — so the app boots instantly even offline. If the
    # download fails (no internet, blocked registry, etc.) we cache that
    # failure and silently fall back to regex-only entity extraction.
    MULTILINGUAL_NER_MODEL = "Davlan/xlm-roberta-base-ner-hrl"

    def __init__(self):
        """Initialize processor with available models"""
        self.spacy_model = None
        self._transformer_ner = None
        self._transformer_ner_load_failed = False
        self.clause_classifier = ClauseClassifier()
        self.summarizer = TextRankSummarizer()
        self.initialize_models()

    def initialize_models(self):
        """Load spaCy eagerly (small/fast/local). Transformer NER stays lazy."""
        if HAS_SPACY:
            try:
                self.spacy_model = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy model not found. Download with: python -m spacy download en_core_web_sm")

    def _get_transformer_ner(self):
        """Lazily load the multilingual transformer NER pipeline, once."""
        if not HAS_TRANSFORMERS or self._transformer_ner_load_failed:
            return None
        if self._transformer_ner is not None:
            return self._transformer_ner
        try:
            self._transformer_ner = pipeline(
                "ner",
                model=self.MULTILINGUAL_NER_MODEL,
                aggregation_strategy="simple",
            )
        except Exception as e:
            print(f"Multilingual NER model unavailable, falling back to regex/spaCy only: {e}")
            self._transformer_ner_load_failed = True
            self._transformer_ner = None
        return self._transformer_ner

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

    # Splits after Nepali danda/!/? always, and after '.' only when it's
    # preceded by a lowercase letter/digit and followed by whitespace +
    # an uppercase/Devanagari letter — avoids shredding "Rs. 50,000",
    # "U.S.", decimals, etc. while still correctly splitting English
    # sentences (previous version only split on Nepali punctuation and
    # silently treated whole English paragraphs as a single "sentence").
    _SENTENCE_SPLIT_PATTERN = re.compile(
        r'(?<=[।!?])\s+|(?<=[a-z0-9)])\.\s+(?=[A-Z\u0900-\u097F])'
    )

    def _split_sentences(self, text: str) -> List[str]:
        parts = self._SENTENCE_SPLIT_PATTERN.split(text.strip())
        return [s.strip() for s in parts if s.strip() and len(s.strip()) > 10]

    def extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Extract clauses/sentences from document, classified by legal type"""
        sentences = self._split_sentences(text)

        clauses = []
        for sentence in sentences[:50]:
            category, confidence = self.clause_classifier.classify(sentence)
            clauses.append({
                "text": sentence,
                "type": category,
                "confidence": confidence if confidence > 0 else 0.5,
            })

        return clauses

    def extract_obligations(self, text: str) -> List[Dict[str, Any]]:
        """Extract obligations/requirements from document"""
        obligations = []

        english_patterns = [
            r'(?:shall|must|should|will|require|mandate|obligate)\s+([^.!?।]+)',
            r'([^.!?।]+?)\s+(?:is required|is mandatory|must be)',
            r'(?:obligation|duty|responsibility|must)\s+(?:is|to)?\s+([^.!?।]+)',
        ]

        nepali_keywords = ['गरनु पर्दछ', 'गर्नु अनिवार्य', 'आवश्यक', 'दायित्व', 'गर्नु जरुरी', 'गरिनेछ', 'गर्न सक्दैन']

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

        for keyword in nepali_keywords:
            matches = re.finditer(r'([^.!?।]*' + re.escape(keyword) + r'[^.!?।]*)', text)
            for match in matches:
                obligation_text = match.group(1).strip()
                if obligation_text and len(obligation_text) > 5:
                    obligations.append({
                        "text": obligation_text,
                        "type": "obligation",
                        "language": "nepali",
                        "confidence": 0.8
                    })

        # Cross-check against the TF-IDF classifier: sentences it independently
        # flags as "obligation" but the regex missed get added too (lower
        # confidence, since only one signal caught them).
        if self.clause_classifier.available:
            for sentence in self._split_sentences(text):
                category, confidence = self.clause_classifier.classify(sentence)
                if category == "obligation" and confidence > 0.15:
                    already_found = any(sentence in o["text"] or o["text"] in sentence for o in obligations)
                    if not already_found:
                        obligations.append({
                            "text": sentence,
                            "type": "obligation",
                            "language": self.detect_language(sentence),
                            "confidence": round(confidence, 2)
                        })

        seen = set()
        unique_obligations = []
        for obl in obligations:
            if obl["text"] not in seen:
                seen.add(obl["text"])
                unique_obligations.append(obl)

        return unique_obligations[:30]

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities (people, organizations, amounts, dates)"""
        entities = []
        language = self.detect_language(text)

        if self.spacy_model and language in ("english", "mixed"):
            doc = self.spacy_model(text[:2000])
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "type": ent.label_.lower(),
                    "confidence": 0.85,
                    "source": "spacy",
                })

        if language in ("nepali", "mixed"):
            ner = self._get_transformer_ner()
            if ner:
                try:
                    for ent in ner(text[:2000]):
                        entities.append({
                            "text": ent["word"],
                            "type": ent["entity_group"].lower(),
                            "confidence": round(float(ent["score"]), 2),
                            "source": "transformer",
                        })
                except Exception:
                    pass

        amount_pattern = r'(?:Rs\.?|NPR|USD|\$|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        for match in re.finditer(amount_pattern, text):
            amount = match.group(0).strip()
            entities.append({
                "text": amount,
                "type": "amount",
                "confidence": 0.9,
                "source": "regex",
            })

        date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
        for match in re.finditer(date_pattern, text):
            entities.append({
                "text": match.group(0),
                "type": "date",
                "confidence": 0.9,
                "source": "regex",
            })

        seen = set()
        unique_entities = []
        for ent in entities:
            key = (ent["text"], ent["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)

        return unique_entities[:20]

    def analyze_complexity(self, text: str) -> int:
        """Analyze document complexity (0-100)"""
        words = len(text.split())
        sentences = len(self._split_sentences(text)) or 1
        avg_word_length = len(text.replace(" ", "")) / max(words, 1)

        score = 0

        if words > 500:
            score += 25
        elif words > 300:
            score += 20
        elif words > 100:
            score += 10

        if avg_word_length > 6:
            score += 25
        elif avg_word_length > 5:
            score += 15

        if sentences > 0:
            avg_sentence_length = words / sentences
            if avg_sentence_length > 20:
                score += 25
            elif avg_sentence_length > 15:
                score += 15

        legal_terms = ['law', 'agreement', 'liability', 'obligation', 'clause',
                        'indemnify', 'whereas', 'thereof', 'herein',
                        'अधिनियम', 'समझौता', 'दायित्व', 'करार']
        for term in legal_terms:
            if term.lower() in text.lower():
                score += 5

        return min(score, 100)

    def analyze_readability(self, text: str) -> int:
        """Analyze document readability (0-100, higher is more readable)"""
        words = len(text.split())
        sentences = len(self._split_sentences(text)) or 1

        if words == 0:
            return 0

        avg_words_per_sentence = words / max(sentences, 1)
        avg_syllables = sum(self.count_syllables(word) for word in text.split()) / words

        score = 100

        if avg_words_per_sentence > 25:
            score -= 30
        elif avg_words_per_sentence > 20:
            score -= 20
        elif avg_words_per_sentence > 15:
            score -= 10

        if avg_syllables > 3:
            score -= 20
        elif avg_syllables > 2.5:
            score -= 10

        return max(score, 0)

    def count_syllables(self, word: str) -> int:
        """Estimate syllable count in a word (Latin-script heuristic)"""
        word = word.lower()
        syllables = 0
        vowels = "aeiouy"
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
        """Generate an extractive summary via TextRank (falls back to
        leading sentences if sklearn/networkx aren't installed)."""
        sentences = self._split_sentences(text)
        return self.summarizer.summarize(sentences, top_n=3, max_chars=400)

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
