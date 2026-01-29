from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.models.database import (
    get_db, Meeting, ActionItem, Decision, KeyPoint
)
from app.services.ai_analyzer import MeetingAnalyzer

router = APIRouter()
analyzer = MeetingAnalyzer()

# Request/Response Models
class MeetingCreate(BaseModel):
    title: str
    raw_notes: str

class ActionItemsResponse(BaseModel):
    id: int
    task: str
    assigned_to: Optional[str]
    deadline: Optional[str]
    status: str

    class Config:
        from_attributes = True

class MeetingResponse(BaseModel):
    id: int
    title: str
    date: datetime
    summary: Optional[str]
    action_items: List[ActionItemsResponse]
    decisions: List[str]
    key_points: List[str]

    class Config:
        from_attributes = True


# Endpoints
@router.post("/meetings", response_model=dict)
async def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    """Create new meeting and analyze notes with AI"""

    # Analyze with AI
    analysis = analyzer.analyze_meeting_notes(meeting.raw_notes)

    # Create meeting record
    db_meeting = Meeting(
        title=meeting.title,
        date=datetime.now(),
        raw_notes=meeting.raw_notes,
        summary=analysis.get("summary"),
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)

    # Store action items
    action_items = []
    for item in analysis["action_items"]:
        db_item = ActionItem(
            meeting_id=db_meeting.id,
            task=item.get("task"),
            assigned_to=item.get("assigned_to"),
            deadline=None # Parse dates properly later
        ) 
        db.add(db_item)
        action_items.append(db_item)

    # Store decisions
    for decision_text in analysis["decisions"]:
        db_decision = Decision(
            meeting_id=db_meeting.id,
            decision=decision_text,
        )
        db.add(db_decision)


    # Store key points
    for point_text in analysis["key_points"]:
        db_point = KeyPoint(
            meeting_id=db_meeting.id,
            point=point_text,
        )
        db.add(db_point)
    
    db.commit()

    return {
        "meeting_id": db_meeting.id,
        "title": db_meeting.title,
        "summary": db_meeting.summary,
        "date": db_meeting.date,
        "action_items_count": len(action_items),
        "message": "Meeting analyzed successfully"
    }

@router.get("/meetings", response_model=List[dict])
async def get_meetings(db: Session = Depends(get_db)):
    """Get all meetings"""
    meetings = db.query(Meeting).order_by(Meeting.date.desc()).all()

    result = []
    for meeting in meetings:
        action_items = db.query(ActionItem).filter(
            ActionItem.meeting_id == meeting.id
        ).all()
        
        result.append({
            "id": meeting.id,
            "title": meeting.title,
            "date": meeting.date,
            "summary": meeting.summary,
            "action_items_count": len(action_items),
            "pending_tasks": len ([a for a in action_items if a.status == "pending"]) # how many items are pending in this list
        })
    
    return result

@router.get("/meetings/{meeting_id}", response_model=dict)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get specific meeting details"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    action_items = db.query(ActionItem).filter( # else fetch from database for action items
        ActionItem.meeting_id == meeting_id
    ).all()
    
    decisions = db.query(Decision).filter(
        Decision.meeting_id == meeting_id
    ).all()

    key_points = db.query(KeyPoint).filter(
        KeyPoint.meeting_id == meeting_id
    ).all()

    return {
        "id": meeting.id,
        "title": meeting.title,
        "date": meeting.date,
        "raw_notes": meeting.raw_notes,
        "summary": meeting.summary,
        "action_items": [
            {
                "id": item.id,
                "task": item.task,
                "assigned_to": item.assigned_to,
                "deadline": item.deadline,
                "status": item.status
            }
            for item in action_items
        ],
        "decisions": [d.decision for d in decisions],
        "key_points": [kp.point for kp in key_points]
    }

@router.get("/action-items", response_model=List[dict])
async def get_all_action_items(db: Session = Depends(get_db)):
    """Get all action items across all meetings"""
    items = db.query(ActionItem).join(Meeting).order_by(
        ActionItem.created_at.desc()
    ).all()

    result = []
    for item in items:
        meeting = db.query(Meeting).filter(Meeting.id == item.meeting_id).first()
        result.append({
            "id": item.id,
            "task": item.task,
            "assigned_to": item.assigned_to,
            "deadline": item.deadline,
            "meeting_title": meeting.title if meeting else "Unkown",
            "meeting_date": meeting.date.isoformat() if meeting else None
        })
    return result

@router.patch("/action-items/{item_id}/complete")
async def complete_action_item(item_id: int, db: Session = Depends(get_db)):
    """Mark action item as complete"""
    item = db.query(ActionItem).filter(ActionItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")

    item.status = "completed"
    db.commit()

    return {"message": "Action item marked as complete"}
