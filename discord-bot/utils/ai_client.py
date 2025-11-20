"""
Anthropic Claude AI client for risk assessment.
"""
import asyncio
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic

from config import settings
from utils.logger import log


class ClaudeClient:
    """Client for Anthropic Claude API."""

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens

    async def analyze_message(
        self,
        message_content: str,
        context: Optional[List[Dict]] = None,
        user_history: Optional[str] = None
    ) -> Dict:
        """
        Analyze a message for radicalization risk using Claude.

        Args:
            message_content: The message text to analyze
            context: Previous messages for context
            user_history: Summary of user's past behavior

        Returns:
            Dict with risk_score, indicators, category, and explanation
        """
        try:
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(
                message_content, context, user_history
            )

            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.3,  # Lower temperature for more consistent analysis
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            analysis = self._parse_response(response.content[0].text)

            log.debug(f"Claude analysis complete: risk_score={analysis.get('risk_score', 0)}")

            return analysis

        except Exception as e:
            log.error(f"Error calling Claude API: {e}")
            return {
                "risk_score": 0,
                "category": "error",
                "indicators": [],
                "explanation": f"Error during analysis: {str(e)}",
                "confidence": 0
            }

    def _build_analysis_prompt(
        self,
        message: str,
        context: Optional[List[Dict]] = None,
        user_history: Optional[str] = None
    ) -> str:
        """Build the prompt for Claude analysis."""

        prompt = f"""You are an expert at analyzing online communication for signs of radicalization and extremism in gaming communities. Your role is to help community moderators identify concerning patterns while minimizing false positives.

Analyze the following message for indicators of radicalization, extremism, hate speech, or violent rhetoric.

MESSAGE TO ANALYZE:
{message}
"""

        if context:
            prompt += f"\n\nPREVIOUS CONTEXT (last {len(context)} messages):\n"
            for i, ctx_msg in enumerate(context[-5:], 1):
                prompt += f"{i}. {ctx_msg.get('author', 'Unknown')}: {ctx_msg.get('content', '')}\n"

        if user_history:
            prompt += f"\n\nUSER HISTORY SUMMARY:\n{user_history}\n"

        prompt += """

ANALYSIS INSTRUCTIONS:
1. Assess the risk level on a scale of 0-100:
   - 0-30: Low risk (normal gaming banter, acceptable communication)
   - 31-60: Medium risk (potentially concerning, monitor closely)
   - 61-85: High risk (serious concern, moderator review needed)
   - 86-100: Critical risk (immediate moderator intervention required)

2. Identify specific indicators from these categories:
   - hate_speech: Dehumanizing language, slurs, bigotry
   - violent_rhetoric: Threats, glorification of violence
   - radicalization: Extremist ideology, recruitment attempts
   - toxicity: Severe harassment, bullying
   - coded_language: Dog whistles, extremist symbols/phrases

3. Consider context:
   - Gaming trash talk vs actual threats
   - Sarcasm and humor vs genuine extremism
   - Cultural references vs hate speech
   - Escalation patterns vs isolated incidents

4. Provide a category (one of):
   - normal: Acceptable communication
   - concerning: Borderline content to monitor
   - hate_speech: Clear hate speech
   - violent_rhetoric: Threats or violence advocacy
   - extremism: Radicalization indicators
   - harassment: Targeted harassment

Respond ONLY with valid JSON in this exact format:
{
  "risk_score": <number 0-100>,
  "category": "<category>",
  "indicators": [
    {
      "type": "<indicator type>",
      "description": "<what was detected>",
      "severity": "<low|medium|high|critical>"
    }
  ],
  "explanation": "<brief explanation of assessment>",
  "confidence": <number 0-100>,
  "requires_human_review": <true|false>
}

Be objective and evidence-based. Account for gaming culture while identifying genuine risks."""

        return prompt

    def _parse_response(self, response_text: str) -> Dict:
        """Parse Claude's JSON response."""
        import json

        try:
            # Try to find JSON in the response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                analysis = json.loads(json_str)

                # Validate required fields
                required_fields = ['risk_score', 'category', 'indicators', 'explanation']
                for field in required_fields:
                    if field not in analysis:
                        raise ValueError(f"Missing required field: {field}")

                # Ensure risk_score is in valid range
                analysis['risk_score'] = max(0, min(100, float(analysis['risk_score'])))

                return analysis
            else:
                raise ValueError("No JSON found in response")

        except Exception as e:
            log.error(f"Error parsing Claude response: {e}")
            log.debug(f"Response was: {response_text}")

            # Return safe default
            return {
                "risk_score": 0,
                "category": "error",
                "indicators": [],
                "explanation": "Failed to parse AI response",
                "confidence": 0,
                "requires_human_review": True
            }

    async def batch_analyze(
        self,
        messages: List[Dict]
    ) -> List[Dict]:
        """
        Analyze multiple messages in batch (with rate limiting).

        Args:
            messages: List of message dicts with 'content', 'context', 'history'

        Returns:
            List of analysis results
        """
        results = []

        for i, msg in enumerate(messages):
            result = await self.analyze_message(
                message_content=msg.get('content', ''),
                context=msg.get('context'),
                user_history=msg.get('history')
            )
            results.append(result)

            # Rate limiting: small delay between calls
            if i < len(messages) - 1:
                await asyncio.sleep(0.5)

        return results


# Global client instance
claude_client = ClaudeClient()
