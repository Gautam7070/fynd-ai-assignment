from sqlalchemy.orm import Session
from .models import Review

def create_review(db: Session, rating, review, summary, action, response):
    db_review = Review(
        rating=rating,
        review=review,
        ai_summary=summary,
        ai_action=action,
        ai_response=response
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_all_reviews(db: Session):
    return db.query(Review).order_by(Review.id.desc()).all()
