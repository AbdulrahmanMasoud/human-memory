"""Emotional salience scoring and emotion detection.

Valence-Arousal model maps emotions to two dimensions:
  - Valence: positive ↔ negative (-1.0 to 1.0)
  - Arousal: calm ↔ excited (0.0 to 1.0)

Salience equation:
  Sal = α|val| + β·aro + γ·rel + δ·nov
"""

import json
import logging

import httpx

logger = logging.getLogger(__name__)

# Emotion → valence/arousal mapping (Russell's Circumplex Model)
EMOTION_MAP: dict[str, dict[str, float]] = {
    "joy": {"valence": 0.8, "arousal": 0.6},
    "happy": {"valence": 0.8, "arousal": 0.6},
    "excitement": {"valence": 0.7, "arousal": 0.9},
    "surprise": {"valence": 0.3, "arousal": 0.8},
    "anger": {"valence": -0.7, "arousal": 0.8},
    "frustrated": {"valence": -0.5, "arousal": 0.7},
    "sadness": {"valence": -0.6, "arousal": 0.3},
    "sad": {"valence": -0.6, "arousal": 0.3},
    "fear": {"valence": -0.7, "arousal": 0.9},
    "anxiety": {"valence": -0.5, "arousal": 0.7},
    "disgust": {"valence": -0.5, "arousal": 0.5},
    "neutral": {"valence": 0.0, "arousal": 0.2},
    "calm": {"valence": 0.2, "arousal": 0.1},
}


class EmotionalSalience:
    """Computes emotional salience scores."""

    def __init__(
        self,
        alpha: float = 0.4,
        beta: float = 0.3,
        gamma: float = 0.2,
        delta: float = 0.1,
    ) -> None:
        self.alpha = alpha  # valence weight
        self.beta = beta  # arousal weight
        self.gamma = gamma  # goal relevance weight
        self.delta = delta  # novelty weight

    def compute_salience(
        self,
        valence: float,
        arousal: float,
        goal_relevance: float = 0.5,
        is_novel: bool = False,
    ) -> float:
        """Compute salience score (0-1)."""
        emotional = self.alpha * abs(valence) + self.beta * arousal
        contextual = self.gamma * goal_relevance + self.delta * (1.0 if is_novel else 0.0)
        return min(1.0, emotional + contextual)

    def modify_decay_rate(self, base_decay: float, salience: float) -> float:
        """High-salience memories decay slower."""
        protection_factor = 1.0 + salience * 2.0
        return base_decay / protection_factor

    def retrieval_boost(self, salience: float, factor: float = 0.5) -> float:
        """Activation boost for high-salience memories during retrieval."""
        return salience * factor


async def detect_emotion(
    text: str,
    api_base: str,
    api_key: str,
    model: str = "gpt-4o-mini",
) -> dict[str, float]:
    """Detect emotion from text using an LLM API.

    Returns: {"valence": float, "arousal": float, "emotion": str}
    """
    prompt = f"""Analyze the emotion in this text and respond with ONLY a JSON object:
{{"emotion": "<one word>", "valence": <-1.0 to 1.0>, "arousal": <0.0 to 1.0>}}

Text: "{text[:500]}"

Respond ONLY with the JSON object, nothing else."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            result = json.loads(content)
            return {
                "valence": float(result.get("valence", 0.0)),
                "arousal": float(result.get("arousal", 0.2)),
                "emotion": str(result.get("emotion", "neutral")),
            }
    except Exception as e:
        logger.warning("Emotion detection failed: %s — using defaults", e)
        return {"valence": 0.0, "arousal": 0.2, "emotion": "neutral"}
