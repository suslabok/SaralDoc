"""
AI Configuration for SaralDoc
Contains all model, language, and processing configurations
"""

# Model Configurations
MODELS_CONFIG = {
    "spacy": {
        "model_name": "en_core_web_sm",
        "version": "3.5.0",
        "enabled": True,
        "purpose": "Named Entity Recognition (NER)",
        "auto_download": True
    },
    "transformers": {
        "model_name": "xlm-roberta-base",
        "version": "1.0",
        "enabled": True,
        "purpose": "Multi-language text classification",
        "cache_dir": ".transformers_cache"
    },
    "bert_nepali": {
        "model_name": "bert-base-multilingual-cased",
        "enabled": False,
        "purpose": "Nepali text understanding (future)"
    }
}

# Language Configurations
LANGUAGES = {
    "nepali": {
        "code": "ne",
        "name": "Nepali",
        "script": "Devanagari",
        "supported": True,
        "keywords_file": "nepali_keywords.json"
    },
    "english": {
        "code": "en",
        "name": "English",
        "script": "Latin",
        "supported": True,
        "keywords_file": "english_keywords.json"
    },
    "hindi": {
        "code": "hi",
        "name": "Hindi",
        "script": "Devanagari",
        "supported": False,
        "keywords_file": "hindi_keywords.json"
    }
}

# Document Categories
DOCUMENT_CATEGORIES = {
    "employment": {
        "name": "Employment Contract",
        "keywords": ["employment", "employee", "salary", "contract", "दायित्व", "वेतन"],
        "risk_level": "medium"
    },
    "loan": {
        "name": "Loan Agreement",
        "keywords": ["loan", "interest", "repayment", "borrower", "ऋण", "ब्याज"],
        "risk_level": "high"
    },
    "service": {
        "name": "Service Agreement",
        "keywords": ["service", "provider", "fees", "duration", "सेवा", "शुल्क"],
        "risk_level": "low"
    },
    "property": {
        "name": "Property/Rental Agreement",
        "keywords": ["rent", "lease", "property", "landlord", "भाडा", "घर"],
        "risk_level": "medium"
    },
    "partnership": {
        "name": "Partnership Agreement",
        "keywords": ["partner", "partnership", "profit", "share", "साझेदार", "लाभ"],
        "risk_level": "high"
    },
    "business": {
        "name": "Business Contract",
        "keywords": ["business", "agreement", "contract", "terms", "व्यापार", "शर्त"],
        "risk_level": "medium"
    }
}

# Extraction Settings
EXTRACTION_CONFIG = {
    "max_text_length": 100000,
    "max_file_size_mb": 10,
    "min_clause_length": 20,
    "max_clauses": 100,
    "max_obligations": 50,
    "max_entities": 100,
    "confidence_threshold": 0.7,
    "supported_formats": [".txt", ".pdf", ".docx"],
    "encoding": "utf-8"
}

# Obligation Types
OBLIGATION_TYPES = {
    "must_do": {
        "description": "Action that must be performed",
        "keywords": ["must", "shall", "obligated", "required", "अनिवार्य"],
        "severity": "high"
    },
    "must_not_do": {
        "description": "Action that must not be performed",
        "keywords": ["must not", "shall not", "prohibited", "forbidden", "गर्न सक्दैन"],
        "severity": "high"
    },
    "conditional": {
        "description": "Conditional obligation",
        "keywords": ["if", "unless", "provided that", "यदि", "जसले गरी"],
        "severity": "medium"
    },
    "right": {
        "description": "Right or permission",
        "keywords": ["may", "can", "have the right", "may choose", "सक्दछ"],
        "severity": "low"
    }
}

# NLP Processing Settings
NLP_SETTINGS = {
    "tokenization": {
        "method": "regex",
        "preserve_punctuation": True,
        "handle_hyphenation": True
    },
    "normalization": {
        "lowercase": False,
        "remove_extra_spaces": True,
        "preserve_nepali_diacritics": True
    },
    "sentence_splitting": {
        "method": "regex",
        "delimiters": ["।", ".", "!", "?", "\n"],
        "min_length": 5
    }
}

# API Settings
API_SETTINGS = {
    "max_concurrent_requests": 10,
    "request_timeout": 300,
    "cache_results": True,
    "cache_ttl": 3600,
    "enable_rate_limiting": True,
    "rate_limit_requests_per_minute": 60
}

# Logging and Monitoring
LOGGING_CONFIG = {
    "level": "INFO",
    "file": "logs/saraldoc.log",
    "max_file_size": 10485760,  # 10MB
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Database Settings (for future implementation)
DATABASE_CONFIG = {
    "type": "sqlite",  # or "postgresql"
    "file": "saraldoc.db",
    "host": "localhost",
    "port": 5432,
    "database": "saraldoc",
    "user": "postgres",
    "password": "password"
}

# Feature Flags
FEATURES = {
    "file_upload": True,
    "text_paste": True,
    "clause_extraction": True,
    "obligation_detection": True,
    "entity_extraction": True,
    "language_detection": True,
    "document_classification": True,
    "summary_generation": True,
    "email_notifications": False,
    "user_authentication": False,
    "advanced_analytics": False
}

# Model Training Settings
TRAINING_CONFIG = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 10,
    "validation_split": 0.2,
    "test_split": 0.1,
    "random_state": 42,
    "early_stopping": True,
    "early_stopping_patience": 3
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "min_accuracy": 0.80,
    "min_precision": 0.75,
    "min_recall": 0.70,
    "min_f1_score": 0.72
}

# Error Handling
ERROR_HANDLING = {
    "log_errors": True,
    "return_partial_results": True,
    "retry_attempts": 3,
    "retry_delay_ms": 1000
}

# Get configuration value
def get_config(key: str, default=None):
    """Get configuration value by key"""
    parts = key.split(".")
    config = globals()
    
    for part in parts:
        if isinstance(config, dict) and part in config:
            config = config[part]
        else:
            return default
    
    return config
