from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import json
import os

load_dotenv()  

# Import AI processor
import processor as processor_module
from processor import processor
from analytics import analytics
from history_db import history_db
from feedback_db import feedback_db
import auth

# Initialize FastAPI app
app = FastAPI(
    title="SaralDoc API",
    description="AI-powered legal document analyzer for Nepali documents",
    version="2.0.0"
)

# Enable CORS for frontend
# ALLOWED_ORIGINS: comma-separated list, e.g. "https://saraldoc.app,https://www.saraldoc.app"
# Falls back to the local dev servers so `python main.py` still works out
# of the box without any .env changes.
_default_origins = "http://localhost:5173,http://localhost:3000"
_allowed_origins = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
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

class GoogleAuthRequest(BaseModel):
    """Request model for Google Sign-In"""
    credential: str  # the ID token from Google Identity Services (frontend)

class ClauseCorrectionRequest(BaseModel):
    """Request model for a user correcting a clause-type prediction"""
    text: str
    language: str = "unknown"
    predicted_type: str
    corrected_type: str
    predicted_confidence: Optional[float] = None
    analysis_id: Optional[int] = None

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
            "spacy": processor_module.HAS_SPACY,
            "transformers": processor_module.HAS_TRANSFORMERS
        }
    }

# ============================================================================
# AUTH (Google Sign-In)
# ============================================================================

@app.post("/auth/google")
async def google_login(body: GoogleAuthRequest, response: Response):
    """Frontend sends the Google ID token here after Google Sign-In
    completes client-side. We verify it with Google, then issue our own
    session cookie so the frontend never has to handle Google tokens
    again after this call."""
    user = auth.verify_google_token(body.credential)
    session_token = auth.create_session_token(user)
    auth.set_session_cookie(response, session_token)
    return {
        "success": True,
        "user": {
            "email": user["email"],
            "name": user["name"],
            "picture": user["picture"],
        },
    }

@app.get("/auth/me")
async def get_me(user: dict = Depends(auth.get_current_user)):
    """Returns the signed-in user's info, or 401 if not signed in."""
    return {
        "email": user["email"],
        "name": user["name"],
        "picture": user["picture"],
    }

@app.post("/auth/logout")
async def logout(response: Response):
    auth.clear_session_cookie(response)
    return {"success": True}
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest, user: Optional[dict] = Depends(auth.get_current_user_optional)):
    """
    Analyze Nepali or English legal text
    Extracts clauses, obligations, entities, and complexity

    Signing in is optional — analysis works either way — but the result is
    only saved to /history when signed in (user['sub']), since there's no
    way to scope an anonymous request to "come back and find this later"
    without either a login or a separate anonymous-session mechanism.
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
        
        # Save to history (only when signed in - see docstring)
        if user:
            history_db.add_analysis({
                'document_name': 'Text Analysis',
                'language': result.get('language', 'unknown'),
                'clauses': result.get('clauses', []),
                'obligations': result.get('obligations', []),
                'entities': result.get('entities', []),
                'complexity_score': complexity,
                'readability_score': readability,
                'summary': request.extract_summary and result.get("summary")
            }, user_id=user["sub"])
        
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

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB — mirrors the frontend's own limit,
                                      # but enforced server-side since a client
                                      # can always bypass frontend-only checks
                                      # by calling the API directly.

@app.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(file: UploadFile = File(...), user: Optional[dict] = Depends(auth.get_current_user_optional)):
    """
    Upload and analyze a legal document
    Supports: PDF, DOCX, TXT
    """
    try:
        # Check file type
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        ext = os.path.splitext(filename)[1].lower()
        if ext not in (".pdf", ".docx", ".txt"):
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT")

        # Save uploaded file
        import tempfile

        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024*1024)} MB)."
            )
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Extract text based on file type
            if ext == '.pdf':
                text = extract_text_from_pdf(tmp_path)
            elif ext == '.docx':
                text = extract_text_from_docx(tmp_path)
            else:
                text = extract_text_from_txt(tmp_path)
            
            # Analyze extracted text
            result = processor.extract_structure(text)
            
            # Calculate complexity
            complexity = processor.analyze_complexity(text)
            readability = processor.analyze_readability(text)
            
            # Save to history (only when signed in - see /analyze docstring)
            if user:
                history_db.add_analysis({
                    'document_name': filename,
                    'language': result.get('language', 'unknown'),
                    'clauses': result.get('clauses', []),
                    'obligations': result.get('obligations', []),
                    'entities': result.get('entities', []),
                    'complexity_score': complexity,
                    'readability_score': readability,
                    'summary': result.get("summary", "")
                }, user_id=user["sub"])
            
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
# Every endpoint below requires a valid session (Depends(auth.get_current_user))
# and every history_db call is scoped to that user's id. Previously these had
# no auth check at all — any client could list, read, or bulk-delete every
# analysis ever run by anyone. See history_db.py's module docstring.

@app.get("/history")
async def get_history(user: dict = Depends(auth.get_current_user)):
    """Get the signed-in user's analysis history"""
    try:
        history = history_db.get_all_history(user_id=user["sub"])
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

@app.get("/history/stats")
async def get_stats(user: dict = Depends(auth.get_current_user)):
    """Get history statistics for the signed-in user"""
    try:
        stats = history_db.get_stats(user_id=user["sub"])
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/history/{analysis_id}")
async def get_analysis(analysis_id: int, user: dict = Depends(auth.get_current_user)):
    """Get a specific analysis by ID — only if it belongs to the signed-in user"""
    try:
        analysis = history_db.get_analysis_by_id(analysis_id, user_id=user["sub"])
        if not analysis:
            # Deliberately the same message whether the id doesn't exist at
            # all or belongs to someone else - don't leak which.
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
async def delete_analysis(analysis_id: int, user: dict = Depends(auth.get_current_user)):
    """Delete an analysis by ID — only if it belongs to the signed-in user"""
    try:
        if history_db.delete_analysis(analysis_id, user_id=user["sub"]):
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
async def clear_history(user: dict = Depends(auth.get_current_user)):
    """Clear the signed-in user's history (does not touch anyone else's)"""
    try:
        if history_db.clear_history(user_id=user["sub"]):
            return {
                "success": True,
                "message": "History cleared"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# FEEDBACK / CLAUSE CORRECTIONS
# ============================================================================
# This is how the Nepali (and English) clause classifier is meant to keep
# improving without more hand-authored/translated seed data: when a user
# corrects a prediction, it's stored as 'pending'. A human reviews pending
# corrections and approves the good ones; export_corrections.py then turns
# approved corrections into datasets/corrections_dataset.csv, which
# trainer.py automatically includes in the next training run.

@app.post("/feedback/clause-correction")
async def submit_clause_correction(body: ClauseCorrectionRequest):
    """Record a user's correction to a clause-type prediction."""
    try:
        cc = processor.clause_classifier
        if cc.using_trained_model:
            valid_types = set(getattr(cc.trained_model, "classes_", []))
        else:
            valid_types = set(getattr(cc, "labels", []))
        if valid_types and body.corrected_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"corrected_type must be one of: {sorted(valid_types)}"
            )
        if not body.text.strip():
            raise HTTPException(status_code=400, detail="text cannot be empty")

        result = feedback_db.add_correction(
            text=body.text,
            language=body.language,
            predicted_type=body.predicted_type,
            corrected_type=body.corrected_type,
            predicted_confidence=body.predicted_confidence,
            analysis_id=body.analysis_id,
        )
        return {"success": True, "correction": result}
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/feedback/corrections")
async def list_clause_corrections(status: Optional[str] = None):
    """List stored corrections, optionally filtered by status
    (pending | approved | rejected)."""
    try:
        corrections = feedback_db.list_corrections(status=status)
        return {"success": True, "corrections": corrections, "total": len(corrections)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/feedback/{correction_id}/approve")
async def approve_correction(correction_id: int):
    """Mark a correction as approved so export_corrections.py will include
    it in the next training run."""
    if feedback_db.set_status(correction_id, "approved"):
        return {"success": True}
    raise HTTPException(status_code=404, detail=f"Correction {correction_id} not found")

@app.post("/feedback/{correction_id}/reject")
async def reject_correction(correction_id: int):
    """Mark a correction as rejected (e.g. it was itself wrong) so it's
    excluded from training."""
    if feedback_db.set_status(correction_id, "rejected"):
        return {"success": True}
    raise HTTPException(status_code=404, detail=f"Correction {correction_id} not found")

@app.get("/feedback/stats")
async def feedback_stats():
    """Pending/approved/rejected correction counts, broken down by language —
    useful for seeing at a glance how much real Nepali signal has accumulated."""
    try:
        return {"success": True, "stats": feedback_db.stats()}
    except Exception as e:
        return {"success": False, "error": str(e)}

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
    """Get information about loaded/available models"""
    import json as _json
    from pathlib import Path as _Path

    clause_model_info = {
        "enabled": processor.clause_classifier.using_trained_model,
        "type": "TF-IDF + Logistic Regression" if processor.clause_classifier.using_trained_model
                else "TF-IDF cosine similarity (seed examples, no trained model found)",
        "purpose": "Legal clause type classification",
    }
    metadata_path = _Path(__file__).parent / "models" / "model_metadata.json"
    if metadata_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                clause_model_info["training_metadata"] = _json.load(f)
        except Exception:
            pass

    return {
        "spacy": {
            "enabled": processor_module.HAS_SPACY,
            "model": "en_core_web_sm",
            "purpose": "English named entity recognition"
        },
        "transformers": {
            "enabled": processor_module.HAS_TRANSFORMERS,
            "model": "xlm-roberta-base",
            "purpose": "Multi-language text classification"
        },
        "clause_classifier": clause_model_info,
        "summarizer": {
            "enabled": processor.summarizer.available,
            "type": "TextRank (TF-IDF sentence graph + PageRank)",
            "purpose": "Extractive summarization"
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
            "history_stats": "/history/stats",
            "submit_correction": "/feedback/clause-correction",
            "list_corrections": "/feedback/corrections",
            "approve_correction": "/feedback/{correction_id}/approve",
            "reject_correction": "/feedback/{correction_id}/reject",
            "feedback_stats": "/feedback/stats"
        }
    }

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
