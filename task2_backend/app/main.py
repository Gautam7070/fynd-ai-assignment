from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from . import models, schemas, crud, llm

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fynd AI Feedback System")

# ✅ Allow ALL cross-origin access (safe for assignment/demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================
# Submit Review Endpoint
# ============================
@app.post("/submit-review", response_model=schemas.ReviewOutput)
def submit_review(
    data: schemas.ReviewInput,
    db: Session = Depends(get_db)
):
    if not data.review.strip():
        raise HTTPException(status_code=400, detail="Empty review")

    # 🔥 FIX: Pass BOTH review AND rating to LLM
    summary, action, response = llm.analyze_review(
        review=data.review,
        rating=data.rating
    )

    crud.create_review(
        db=db,
        rating=data.rating,
        review=data.review,
        summary=summary,
        action=action,
        response=response
    )

    return {
        "message": "Review submitted successfully",
        "ai_response": response
    }


# ============================
# Admin Reviews Endpoint
# ============================
@app.get("/admin/reviews", response_model=list[schemas.AdminReview])
def admin_reviews(db: Session = Depends(get_db)):
    reviews = crud.get_all_reviews(db)
    return [
        {
            "rating": r.rating,
            "review": r.review,
            "ai_summary": r.ai_summary,
            "ai_action": r.ai_action
        }
        for r in reviews
    ]


# ============================
# Debug Endpoint (optional)
# ============================
@app.get("/debug/config")
def debug_config():
    return {
        "llm_loaded": True,
        "env_loaded": llm.api_key is not None
    }
