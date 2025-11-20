"""
Tests for risk assessment service.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.risk_assessment import RiskAssessmentService


@pytest.fixture
def risk_service():
    """Create risk service instance."""
    return RiskAssessmentService()


@pytest.fixture
def mock_db():
    """Mock database."""
    with patch('services.risk_assessment.db') as mock:
        yield mock


@pytest.fixture
def mock_claude():
    """Mock Claude client."""
    with patch('services.risk_assessment.claude_client') as mock:
        yield mock


class TestKeywordAnalysis:
    """Tests for keyword-based risk analysis."""

    def test_keyword_analysis_normal_message(self, risk_service):
        """Test that normal messages get low risk scores."""
        message = "Hey everyone, excited for the new game release!"
        result = risk_service._keyword_analysis(message)

        assert result['risk_score'] < 30
        assert result['category'] == 'normal'
        assert len(result['indicators']) == 0

    def test_keyword_analysis_empty_message(self, risk_service):
        """Test that empty messages get zero risk score."""
        message = ""
        result = risk_service._keyword_analysis(message)

        assert result['risk_score'] == 0
        assert result['category'] == 'normal'


class TestCombineAssessments:
    """Tests for combining keyword and AI assessments."""

    def test_combine_assessments_weights(self, risk_service):
        """Test that AI analysis is weighted more heavily."""
        keyword_result = {
            'risk_score': 100,
            'category': 'high_risk',
            'indicators': [{'type': 'keyword'}],
            'explanation': 'Keyword match',
            'confidence': 60
        }

        ai_result = {
            'risk_score': 0,
            'category': 'normal',
            'indicators': [],
            'explanation': 'No issues found',
            'confidence': 90
        }

        combined = risk_service._combine_assessments(keyword_result, ai_result)

        # Should be weighted 70% AI (0) + 30% keyword (100) = 30
        assert combined['risk_score'] == pytest.approx(30, abs=0.1)
        assert combined['category'] == 'normal'  # AI category takes precedence

    def test_combine_assessments_combines_indicators(self, risk_service):
        """Test that indicators from both sources are combined."""
        keyword_result = {
            'risk_score': 50,
            'category': 'concerning',
            'indicators': [{'type': 'keyword', 'pattern': 'test'}],
            'explanation': 'Test',
            'confidence': 60
        }

        ai_result = {
            'risk_score': 40,
            'category': 'concerning',
            'indicators': [{'type': 'ai', 'description': 'test'}],
            'explanation': 'AI test',
            'confidence': 80
        }

        combined = risk_service._combine_assessments(keyword_result, ai_result)

        assert len(combined['indicators']) == 2
        assert combined['keyword_matches'] == 1


@pytest.mark.asyncio
class TestAssessMessage:
    """Tests for full message assessment."""

    async def test_assess_empty_message(self, risk_service, mock_db):
        """Test that empty messages return safe assessment."""
        result = await risk_service.assess_message(
            message_id=1,
            message_content="",
            user_id=1,
            server_id=1
        )

        assert result['risk_score'] == 0
        assert result['category'] == 'normal'

    async def test_assess_message_calls_ai_for_long_messages(
        self,
        risk_service,
        mock_db,
        mock_claude
    ):
        """Test that AI is called for longer messages."""
        # Setup
        mock_claude.analyze_message = AsyncMock(return_value={
            'risk_score': 25,
            'category': 'normal',
            'indicators': [],
            'explanation': 'Normal conversation',
            'confidence': 85
        })

        mock_db.fetchval = AsyncMock(return_value=1)
        mock_db.fetch = AsyncMock(return_value=[])
        mock_db.execute = AsyncMock()

        # Long message should trigger AI analysis
        long_message = "This is a longer message " * 10

        result = await risk_service.assess_message(
            message_id=1,
            message_content=long_message,
            user_id=1,
            server_id=1
        )

        # Verify AI was called
        mock_claude.analyze_message.assert_called_once()

    async def test_assess_message_stores_assessment(
        self,
        risk_service,
        mock_db,
        mock_claude
    ):
        """Test that assessment is stored in database."""
        # Setup
        mock_claude.analyze_message = AsyncMock(return_value={
            'risk_score': 75,
            'category': 'high_risk',
            'indicators': [{'type': 'test', 'description': 'test indicator', 'severity': 'high'}],
            'explanation': 'Test explanation',
            'confidence': 90
        })

        mock_db.fetchval = AsyncMock(side_effect=[1, 0, 123])  # user check, history check, assessment_id
        mock_db.fetch = AsyncMock(return_value=[])
        mock_db.execute = AsyncMock()

        result = await risk_service.assess_message(
            message_id=1,
            message_content="Test message with risk indicators",
            user_id=1,
            server_id=1
        )

        # Verify assessment was stored
        assert mock_db.fetchval.called
        assert result['assessment_id'] == 123


class TestHelperMethods:
    """Tests for helper methods."""

    def test_create_safe_assessment(self, risk_service):
        """Test creating safe assessment."""
        assessment = risk_service._create_safe_assessment(
            message_id=1,
            user_id=2,
            server_id=3,
            risk_score=15,
            category='normal'
        )

        assert assessment['message_id'] == 1
        assert assessment['user_id'] == 2
        assert assessment['server_id'] == 3
        assert assessment['risk_score'] == 15
        assert assessment['category'] == 'normal'
        assert assessment['indicators'] == []
