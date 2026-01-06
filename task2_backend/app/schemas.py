from pydantic import BaseModel, Field

class ReviewInput(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str = Field(min_length=1, max_length=2000)

class ReviewOutput(BaseModel):
    message: str
    ai_response: str

class AdminReview(BaseModel):
    rating: int
    review: str
    ai_summary: str
    ai_action: str
