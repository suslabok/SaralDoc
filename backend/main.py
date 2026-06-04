"""
SaralDoc API Server - Main FastAPI Application
Connects frontend UI to AI text processing pipeline
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import PyPDF2
from docx import Document
import json
import os

# Import AI processor
from processor import processor
from analytics import analytics
from history_db import history_db

# Initialize FastAPI app
app = FastAPI(
    title="SaralDoc API",
    description="AI-powered legal document analyzer for Nepali documents",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request model for text analysis"""
    text: str
    language: Optional[str] = "auto"
    extract_summary: Optional[bool] = True

class ClauseResult(BaseModel):
    """A single clause from document"""
    clause: str
    type: str
    confidence: float

class ObligationResult(BaseModel):
    """A single obligation found"""
    obligation: str
    type: str
    language: str
    confidence: float

class EntityResult(BaseModel):
    """A named entity"""
    text: str
    type: str
    confidence: float

class AnalyzeResponse(BaseModel):
    """Response model for analysis"""
    success: bool
    clauses: List[ClauseResult]
    obligations: List[ObligationResult]
    entities: List[EntityResult]
    language: str
    complexity_score: int
    readability_score: int
    summary: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Check if API and models are loaded"""
    return {
        "status": "healthy",
        "message": "SaralDoc API is running",
        "version": "2.0.0",
        "models": {
            "spacy": processor.HAS_SPACY,
            "transformers": processor.HAS_TRANSFORMERS
        }
    }

# ============================================================================
# TEXT ANALYSIS ENDPOINT
# ============================================================================

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze Nepali or English legal text
    Extracts clauses, obligations, entities, and complexity
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 100000:
            raise HTTPException(status_code=400, detail="Text too long (max 100,000 chars)")
        
        # Process text with AI
        result = processor.extract_structure(request.text)
        
        # Calculate complexity
        complexity = processor.analyze_complexity(request.text)
        readability = processor.analyze_readability(request.text)
        
        # Save to history
        history_db.add_analysis({
            'document_name': 'Text Analysis',
            'language': result.get('language', 'unknown'),
            'clauses': result.get('clauses', []),
            'obligations': result.get('obligations', []),
            'entities': result.get('entities', []),
            'complexity_score': complexity,
            'readability_score': readability,
            'summary': request.extract_summary and result.get("summary")
        })
        
        # Format response
        return AnalyzeResponse(
            success=True,
            clauses=[
                ClauseResult(
                    clause=c.get("text", ""),
                    type=c.get("type", "clause"),
                    confidence=c.get("confidence", 0.7)
                )
                for c in result.get("clauses", [])
            ],
            obligations=[
                ObligationResult(
                    obligation=o.get("text", ""),
                    type=o.get("type", "obligation"),
                    language=o.get("language", "nepali"),
                    confidence=o.get("confidence", 0.7)
                )
                for o in result.get("obligations", [])
            ],
            entities=[
                EntityResult(
                    text=e.get("text", ""),
                    type=e.get("type", "person"),
                    confidence=e.get("confidence", 0.7)
                )
                for e in result.get("entities", [])
            ],
            language=result.get("language", "nepali"),
            complexity_score=complexity,
            readability_score=readability,
            summary=request.extract_summary and result.get("summary")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AnalyzeResponse(
            success=False,
            clauses=[],
            obligations=[],
            entities=[],
            language="unknown",
            complexity_score=0,
            readability_score=0,
            error=str(e)
        )

# ============================================================================
# FILE UPLOAD ENDPOINT
# ============================================================================

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        text = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return '\n'.join(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return '\n'.join(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading DOCX: {str(e)}")

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading TXT: {str(e)}")

@app.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(file: UploadFile = File(...)):
    """
    Upload and analyze a legal document
    Supports: PDF, DOCX, TXT
    """
    try:
        # Check file type
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Save uploaded file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Extract text based on file type
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(tmp_path)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(tmp_path)
            elif filename.endswith('.txt'):
                text = extract_text_from_txt(tmp_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT")
            
            # Analyze extracted text
            result = processor.extract_structure(text)
            
            # Calculate complexity
            complexity = processor.analyze_complexity(text)
            readability = processor.analyze_readability(text)
            
            # Save to history
            history_db.add_analysis({
                'document_name': filename,
                'language': result.get('language', 'unknown'),
                'clauses': result.get('clauses', []),
                'obligations': result.get('obligations', []),
                'entities': result.get('entities', []),
                'complexity_score': complexity,
                'readability_score': readability,
                'summary': result.get("summary", "")
            })
            
            return AnalyzeResponse(
                success=True,
                clauses=[
                    ClauseResult(
                        clause=c.get("text", ""),
                        type=c.get("type", "clause"),
                        confidence=c.get("confidence", 0.7)
                    )
                    for c in result.get("clauses", [])
                ],
                obligations=[
                    ObligationResult(
                        obligation=o.get("text", ""),
                        type=o.get("type", "obligation"),
                        language=o.get("language", "nepali"),
                        confidence=o.get("confidence", 0.7)
                    )
                    for o in result.get("obligations", [])
                ],
                entities=[
                    EntityResult(
                        text=e.get("text", ""),
                        type=e.get("type", "person"),
                        confidence=e.get("confidence", 0.7)
                    )
                    for e in result.get("entities", [])
                ],
                language=result.get("language", "nepali"),
                complexity_score=complexity,
                readability_score=readability,
                summary=result.get("summary")
            )
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        return AnalyzeResponse(
            success=False,
            clauses=[],
            obligations=[],
            entities=[],
            language="unknown",
            complexity_score=0,
            readability_score=0,
            error=str(e)
        )

# ============================================================================
# HISTORY ENDPOINTS
# ============================================================================

@app.get("/history")
async def get_history():
    """Get all analysis history"""
    try:
        history = history_db.get_all_history()
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/history/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Get specific analysis by ID"""
    try:
        analysis = history_db.get_analysis_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"Analysis {analysis_id} not found")
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/history/{analysis_id}")
async def delete_analysis(analysis_id: int):
    """Delete analysis by ID"""
    try:
        if history_db.delete_analysis(analysis_id):
            return {
                "success": True,
                "message": f"Analysis {analysis_id} deleted"
            }
        else:
            raise ValueError(f"Analysis {analysis_id} not found")
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/history")
async def clear_history():
    """Clear all history"""
    try:
        if history_db.clear_history():
            return {
                "success": True,
                "message": "History cleared"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/history/stats")
async def get_stats():
    """Get history statistics"""
    try:
        stats = history_db.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": ["nepali", "english", "mixed"],
        "nlp_library": "spacy",
        "ml_library": "transformers"
    }

@app.get("/models")
async def get_models_info():
    """Get information about loaded models"""
    return {
        "spacy": {
            "enabled": processor.HAS_SPACY,
            "model": "en_core_web_sm",
            "purpose": "Named Entity Recognition"
        },
        "transformers": {
            "enabled": processor.HAS_TRANSFORMERS,
            "model": "xlm-roberta-base",
            "purpose": "Multi-language text classification"
        },
        "nltk": {
            "enabled": True,
            "purpose": "Text processing & analysis"
        }
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Welcome message"""
    return {
        "name": "SaralDoc",
        "description": "AI-powered legal document analyzer",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "analyze_file": "/analyze-file",
            "languages": "/languages",
            "models": "/models",
            "docs": "/docs",
            "history": "/history",
            "history_id": "/history/{analysis_id}",
            "delete_history_id": "/history/{analysis_id}",
            "clear_history": "/history",
            "history_stats": "/history/stats"
        }
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
