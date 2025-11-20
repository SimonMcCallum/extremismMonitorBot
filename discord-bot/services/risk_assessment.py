"""
Risk assessment service combining AI analysis with rule-based detection.
"""
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from config import settings
from utils.logger import log
from utils.database import db
from utils.ai_client import claude_client


class RiskAssessmentService:
    """Service for assessing radicalization risk in messages."""

    # Keywords associated with different risk categories
    # This is a simplified example - production would use more sophisticated patterns
    RISK_KEYWORDS = {
        "hate_speech": [
            r"\b(racial slur patterns)\b",  # Actual slurs would be here
            r"\bdehumaniz(e|ing)\b",
            r"\bsubhuman\b",
        ],
        "violent_rhetoric": [
            r"\b(kill|murder|massacre)\s+(all|every)\b",
            r"\bviolent\s+revolution\b",
            r"\bblood\s+and\s+soil\b",
        ],
        "extremism": [
            r"\b(white|black|any)\s+supremac(y|ist)\b",
            r"\bracial\s+war\b",
            r"\bday\s+of\s+the\s+rope\b",
        ],
    }

    def __init__(self):
        self.claude = claude_client

    async def assess_message(
        self,
        message_id: int,
        message_content: str,
        user_id: int,
        server_id: int,
        context_messages: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Comprehensive risk assessment for a message.

        Args:
            message_id: Database ID of the message
            message_content: The message text
            user_id: Database ID of the user
            server_id: Database ID of the server
            context_messages: Previous messages for context

        Returns:
            Assessment result with risk score and indicators
        """
        try:
            # Skip empty messages
            if not message_content or not message_content.strip():
                return self._create_safe_assessment(
                    message_id, user_id, server_id, 0, "normal"
                )

            # 1. Get user history
            user_history = await self._get_user_history_summary(user_id)

            # 2. Keyword-based analysis (fast, cheap)
            keyword_result = self._keyword_analysis(message_content)

            # 3. Decide if we need AI analysis
            needs_ai_analysis = (
                len(message_content) > 50 or  # Longer messages
                keyword_result['risk_score'] > 30 or  # Keywords detected
                await self._user_has_history(user_id)  # User has past flags
            )

            if needs_ai_analysis and settings.enable_risk_monitoring:
                # 4. AI-powered analysis using Claude
                ai_result = await self.claude.analyze_message(
                    message_content=message_content,
                    context=context_messages,
                    user_history=user_history
                )

                # 5. Combine results
                final_assessment = self._combine_assessments(
                    keyword_result, ai_result
                )
            else:
                # Use keyword-only assessment
                final_assessment = keyword_result

            # 6. Store assessment in database
            assessment_id = await self._store_assessment(
                message_id=message_id,
                user_id=user_id,
                server_id=server_id,
                assessment=final_assessment
            )

            final_assessment['assessment_id'] = assessment_id

            # 7. Generate alert if needed
            if final_assessment['risk_score'] >= settings.risk_high_threshold:
                await self._generate_alert(
                    assessment_id=assessment_id,
                    user_id=user_id,
                    server_id=server_id,
                    risk_score=final_assessment['risk_score'],
                    category=final_assessment.get('category', 'unknown')
                )

            log.info(
                f"Risk assessment complete: message_id={message_id}, "
                f"risk_score={final_assessment['risk_score']:.1f}"
            )

            return final_assessment

        except Exception as e:
            log.error(f"Error in risk assessment: {e}")
            return self._create_safe_assessment(
                message_id, user_id, server_id, 0, "error"
            )

    def _keyword_analysis(self, message_content: str) -> Dict:
        """
        Fast keyword-based risk analysis.

        Returns:
            Dict with risk_score, category, and matched keywords
        """
        message_lower = message_content.lower()
        matched_patterns = []
        total_severity = 0

        for category, patterns in self.RISK_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    matched_patterns.append({
                        "type": category,
                        "pattern": pattern,
                        "severity": "medium"
                    })
                    total_severity += 30  # Each match adds to score

        # Calculate risk score based on matches
        risk_score = min(100, total_severity)

        # Determine category
        if risk_score >= 70:
            category = "high_risk"
        elif risk_score >= 40:
            category = "concerning"
        else:
            category = "normal"

        return {
            "risk_score": risk_score,
            "category": category,
            "indicators": matched_patterns,
            "explanation": f"Keyword analysis: {len(matched_patterns)} patterns matched",
            "confidence": 60 if matched_patterns else 80,
            "method": "keyword"
        }

    def _combine_assessments(
        self,
        keyword_result: Dict,
        ai_result: Dict
    ) -> Dict:
        """
        Combine keyword and AI analysis results.

        Gives more weight to AI analysis but considers keyword matches.
        """
        # Weight: 70% AI, 30% keyword
        combined_score = (
            ai_result.get('risk_score', 0) * 0.7 +
            keyword_result.get('risk_score', 0) * 0.3
        )

        # Combine indicators
        all_indicators = (
            keyword_result.get('indicators', []) +
            ai_result.get('indicators', [])
        )

        # Use AI category if available, otherwise keyword category
        category = ai_result.get('category', keyword_result.get('category', 'normal'))

        return {
            "risk_score": combined_score,
            "category": category,
            "indicators": all_indicators,
            "explanation": ai_result.get('explanation', keyword_result.get('explanation')),
            "confidence": ai_result.get('confidence', keyword_result.get('confidence', 50)),
            "ai_analysis": ai_result.get('explanation'),
            "keyword_matches": len(keyword_result.get('indicators', [])),
            "requires_human_review": ai_result.get('requires_human_review', False)
        }

    async def _get_user_history_summary(self, user_id: int) -> Optional[str]:
        """Get summary of user's past risk assessments."""
        try:
            # Get recent assessments for this user
            recent = await db.fetch(
                """
                SELECT risk_score, risk_category, created_at
                FROM risk_assessments
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 10
                """,
                user_id
            )

            if not recent:
                return None

            # Calculate average risk score
            avg_score = sum(r['risk_score'] for r in recent) / len(recent)

            # Count flagged assessments
            flagged_count = sum(1 for r in recent if r['risk_score'] > 60)

            summary = (
                f"User has {len(recent)} recent assessments. "
                f"Average risk score: {avg_score:.1f}. "
                f"Flagged content: {flagged_count} times."
            )

            return summary

        except Exception as e:
            log.error(f"Error getting user history: {e}")
            return None

    async def _user_has_history(self, user_id: int) -> bool:
        """Check if user has any flagged assessments."""
        try:
            count = await db.fetchval(
                """
                SELECT COUNT(*)
                FROM risk_assessments
                WHERE user_id = $1 AND flagged = true
                """,
                user_id
            )
            return count > 0
        except Exception as e:
            log.error(f"Error checking user history: {e}")
            return False

    async def _store_assessment(
        self,
        message_id: int,
        user_id: int,
        server_id: int,
        assessment: Dict
    ) -> int:
        """Store risk assessment in database."""
        try:
            query = """
                INSERT INTO risk_assessments (
                    message_id,
                    user_id,
                    server_id,
                    risk_score,
                    risk_category,
                    indicators,
                    ai_analysis,
                    flagged,
                    created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                RETURNING id
            """

            flagged = assessment['risk_score'] >= settings.risk_medium_threshold

            assessment_id = await db.fetchval(
                query,
                message_id,
                user_id,
                server_id,
                assessment['risk_score'],
                assessment.get('category'),
                assessment.get('indicators', []),
                assessment.get('explanation'),
                flagged
            )

            # Update user's risk score (rolling average)
            await self._update_user_risk_score(user_id, assessment['risk_score'])

            return assessment_id

        except Exception as e:
            log.error(f"Error storing assessment: {e}")
            return None

    async def _update_user_risk_score(self, user_id: int, new_score: float):
        """Update user's overall risk score (rolling average)."""
        try:
            # Get user's recent risk scores
            recent_scores = await db.fetch(
                """
                SELECT risk_score
                FROM risk_assessments
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT 20
                """,
                user_id
            )

            if recent_scores:
                # Calculate rolling average
                avg_score = sum(r['risk_score'] for r in recent_scores) / len(recent_scores)

                # Update user record
                await db.execute(
                    """
                    UPDATE users
                    SET risk_score = $1,
                        last_seen = NOW()
                    WHERE id = $2
                    """,
                    avg_score,
                    user_id
                )

        except Exception as e:
            log.error(f"Error updating user risk score: {e}")

    async def _generate_alert(
        self,
        assessment_id: int,
        user_id: int,
        server_id: int,
        risk_score: float,
        category: str
    ):
        """Generate an alert for moderators."""
        try:
            # Determine severity based on risk score
            if risk_score >= settings.risk_critical_threshold:
                severity = "critical"
                title = "🚨 Critical Risk Detected"
            elif risk_score >= settings.risk_high_threshold:
                severity = "high"
                title = "⚠️ High Risk Content Detected"
            else:
                severity = "medium"
                title = "⚡ Medium Risk Content Detected"

            # Get user info for description
            user_info = await db.fetchrow(
                "SELECT discord_user_id, username FROM users WHERE id = $1",
                user_id
            )

            description = (
                f"User {user_info['username']} (ID: {user_info['discord_user_id']}) "
                f"posted content with risk score {risk_score:.1f}. "
                f"Category: {category}"
            )

            # Insert alert
            query = """
                INSERT INTO alerts (
                    server_id,
                    user_id,
                    assessment_id,
                    severity,
                    title,
                    description,
                    status,
                    created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, 'open', NOW())
                RETURNING id
            """

            alert_id = await db.fetchval(
                query,
                server_id,
                user_id,
                assessment_id,
                severity,
                title,
                description
            )

            log.warning(f"Alert generated: alert_id={alert_id}, severity={severity}, risk_score={risk_score}")

            return alert_id

        except Exception as e:
            log.error(f"Error generating alert: {e}")
            return None

    def _create_safe_assessment(
        self,
        message_id: int,
        user_id: int,
        server_id: int,
        risk_score: float,
        category: str
    ) -> Dict:
        """Create a safe/default assessment."""
        return {
            "message_id": message_id,
            "user_id": user_id,
            "server_id": server_id,
            "risk_score": risk_score,
            "category": category,
            "indicators": [],
            "explanation": "Default assessment",
            "confidence": 0
        }


# Global service instance
risk_service = RiskAssessmentService()
