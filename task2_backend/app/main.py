from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, schemas, crud, llm

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fynd AI Feedback System")

# ✅ Allow ALL cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods
    allow_headers=["*"],          # allow all headers
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/submit-review", response_model=schemas.ReviewOutput)
def submit_review(
    data: schemas.ReviewInput,
    db: Session = Depends(get_db)
):
    if not data.review.strip():
        raise HTTPException(status_code=400, detail="Empty review")

    summary, action, response = llm.analyze_review(data.review)

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


@app.get("/debug/config")
def debug_config():
    from . import llm
    return {
        "api_key_loaded": llm.api_key is not None,
        "api_key_prefix": str(llm.api_key)[:5] if llm.api_key else None,
        "env_path": llm.env_path
    }

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
