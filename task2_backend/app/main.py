from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging
import sys

from .database import SessionLocal, engine
from . import models, schemas, crud, llm

# ============================
# Logging Configuration
# ============================
logger = logging.getLogger("fynd_ai_backend")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ============================
# Create DB tables
# ============================
models.Base.metadata.create_all(bind=engine)
logger.info("Database tables verified/created")

# ============================
# FastAPI App
# ============================
app = FastAPI(title="Fynd AI Feedback System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# DB Dependency
# ============================
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
    logger.info(
        f"POST /submit-review | rating={data.rating} | review='{data.review[:50]}'"
    )

    if not data.review.strip():
        logger.warning("Rejected empty review submission")
        raise HTTPException(status_code=400, detail="Empty review")

    # LLM processing
    logger.info("Calling LLM for review analysis")
    summary, action, response = llm.analyze_review(
        review=data.review,
        rating=data.rating
    )

    # Save to DB
    crud.create_review(
        db=db,
        rating=data.rating,
        review=data.review,
        summary=summary,
        action=action,
        response=response
    )

    logger.info("Review successfully saved to database")

    return {
        "message": "Review submitted successfully",
        "ai_response": response
    }

# ============================
# Admin Reviews Endpoint
# ============================
@app.get("/admin/reviews", response_model=list[schemas.AdminReview])
def admin_reviews(db: Session = Depends(get_db)):
    logger.info("GET /admin/reviews requested")

    reviews = crud.get_all_reviews(db)
    logger.info(f"Returned {len(reviews)} reviews")

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
# Debug Endpoint
# ============================
@app.get("/debug/config")
def debug_config():
    logger.info("GET /debug/config called")
    return {
        "llm_loaded": True,
        "env_loaded": llm.api_key is not None
    }
