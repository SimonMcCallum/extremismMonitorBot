"""
Risk management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import RiskAssessment, Alert, User, Server


router = APIRouter()


# Pydantic schemas
class RiskIndicator(BaseModel):
    """Schema for risk indicator."""
    type: str
    description: str
    severity: str


class RiskAssessmentResponse(BaseModel):
    """Schema for risk assessment response."""
    id: int
    message_id: Optional[int]
    user_id: int
    server_id: int
    risk_score: float
    risk_category: Optional[str]
    indicators: List[dict]
    ai_analysis: Optional[str]
    flagged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Schema for alert response."""
    id: int
    server_id: int
    user_id: int
    severity: str
    title: str
    description: Optional[str]
    status: str
    created_at: datetime
    username: Optional[str] = None

    class Config:
        from_attributes = True


class RiskStatsResponse(BaseModel):
    """Schema for risk statistics."""
    total_assessments: int
    flagged_count: int
    average_risk_score: float
    high_risk_users: int
    active_alerts: int


@router.get("/assessments", response_model=List[RiskAssessmentResponse])
async def get_risk_assessments(
    server_id: Optional[int] = None,
    user_id: Optional[int] = None,
    flagged_only: bool = False,
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk assessments with optional filtering.

    Args:
        server_id: Filter by server ID
        user_id: Filter by user ID
        flagged_only: Only return flagged assessments
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    query = select(RiskAssessment).order_by(desc(RiskAssessment.created_at))

    # Apply filters
    filters = []
    if server_id:
        filters.append(RiskAssessment.server_id == server_id)
    if user_id:
        filters.append(RiskAssessment.user_id == user_id)
    if flagged_only:
        filters.append(RiskAssessment.flagged == True)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    assessments = result.scalars().all()

    return assessments


@router.get("/assessments/{assessment_id}", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    assessment_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific risk assessment by ID."""
    result = await db.execute(
        select(RiskAssessment).where(RiskAssessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")

    return assessment


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    server_id: Optional[int] = None,
    status: str = "open",
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get alerts with optional filtering.

    Args:
        server_id: Filter by server ID
        status: Filter by status (open, acknowledged, resolved)
        severity: Filter by severity (low, medium, high, critical)
        skip: Number of records to skip
        limit: Maximum number of records to return
    """
    query = (
        select(Alert, User.username)
        .join(User, Alert.user_id == User.id)
        .order_by(desc(Alert.created_at))
    )

    # Apply filters
    filters = []
    if server_id:
        filters.append(Alert.server_id == server_id)
    if status:
        filters.append(Alert.status == status)
    if severity:
        filters.append(Alert.severity == severity)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    alerts_with_users = result.all()

    # Transform results
    alert_responses = []
    for alert, username in alerts_with_users:
        alert_dict = {
            "id": alert.id,
            "server_id": alert.server_id,
            "user_id": alert.user_id,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "status": alert.status,
            "created_at": alert.created_at,
            "username": username
        }
        alert_responses.append(AlertResponse(**alert_dict))

    return alert_responses


@router.patch("/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: int,
    status: str,
    resolution_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the status of an alert.

    Args:
        alert_id: ID of the alert
        status: New status (open, acknowledged, resolved)
        resolution_notes: Optional notes about the resolution
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Update status
    alert.status = status
    if status == "resolved":
        alert.resolved_at = datetime.utcnow()
        if resolution_notes:
            alert.resolution_notes = resolution_notes

    await db.commit()

    return {"message": "Alert status updated", "alert_id": alert_id, "status": status}


@router.get("/stats", response_model=RiskStatsResponse)
async def get_risk_stats(
    server_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk assessment statistics.

    Args:
        server_id: Optional server ID to filter stats
    """
    # Build base query
    assessment_query = select(RiskAssessment)
    alert_query = select(Alert)

    if server_id:
        assessment_query = assessment_query.where(RiskAssessment.server_id == server_id)
        alert_query = alert_query.where(Alert.server_id == server_id)

    # Total assessments
    total_result = await db.execute(
        select(func.count()).select_from(assessment_query.subquery())
    )
    total_assessments = total_result.scalar() or 0

    # Flagged count
    flagged_result = await db.execute(
        select(func.count()).select_from(
            assessment_query.where(RiskAssessment.flagged == True).subquery()
        )
    )
    flagged_count = flagged_result.scalar() or 0

    # Average risk score
    avg_result = await db.execute(
        select(func.avg(RiskAssessment.risk_score)).select_from(
            assessment_query.subquery()
        )
    )
    average_risk_score = float(avg_result.scalar() or 0)

    # High risk users (risk_score > 70)
    user_query = select(User)
    if server_id:
        # For server-specific stats, we'd need to join through messages
        # Simplified for now
        pass

    high_risk_result = await db.execute(
        select(func.count()).select_from(
            select(User).where(User.risk_score > 70).subquery()
        )
    )
    high_risk_users = high_risk_result.scalar() or 0

    # Active alerts
    active_alerts_result = await db.execute(
        select(func.count()).select_from(
            alert_query.where(Alert.status == "open").subquery()
        )
    )
    active_alerts = active_alerts_result.scalar() or 0

    return RiskStatsResponse(
        total_assessments=total_assessments,
        flagged_count=flagged_count,
        average_risk_score=average_risk_score,
        high_risk_users=high_risk_users,
        active_alerts=active_alerts
    )


@router.get("/users/{user_id}/risk-history")
async def get_user_risk_history(
    user_id: int,
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk assessment history for a specific user.

    Args:
        user_id: User ID
        limit: Maximum number of records to return
    """
    result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.user_id == user_id)
        .order_by(desc(RiskAssessment.created_at))
        .limit(limit)
    )
    assessments = result.scalars().all()

    if not assessments:
        return {
            "user_id": user_id,
            "assessments": [],
            "summary": {
                "total": 0,
                "average_score": 0,
                "highest_score": 0,
                "flagged_count": 0
            }
        }

    # Calculate summary
    scores = [a.risk_score for a in assessments]
    flagged = [a for a in assessments if a.flagged]

    return {
        "user_id": user_id,
        "assessments": [
            {
                "id": a.id,
                "risk_score": a.risk_score,
                "category": a.risk_category,
                "flagged": a.flagged,
                "created_at": a.created_at
            }
            for a in assessments
        ],
        "summary": {
            "total": len(assessments),
            "average_score": sum(scores) / len(scores),
            "highest_score": max(scores),
            "flagged_count": len(flagged)
        }
    }
