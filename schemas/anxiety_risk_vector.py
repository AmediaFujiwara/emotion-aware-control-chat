"""
Pydantic models for the Anxiety Risk Vector (3-axis structural risk model).
"""

from pydantic import BaseModel, Field, field_validator


class ResponsePolicy(BaseModel):
    """AI response strategy derived from the 3-axis risk vector."""

    primary_strategy: str = Field(description="主方針")
    secondary_strategy: str = Field(description="副方針")
    avoid: list[str] = Field(default_factory=list, description="避けること")
    recommended_response_style: str = Field(description="推奨回答スタイル")
    should_use_ni: bool = Field(default=False, description="NI（非介入）を使うか")
    ni_reason: str = Field(default="", description="NIを使う理由")


class AnxietyRiskVector(BaseModel):
    """
    Structural risk vector decomposing anxiety into 3 axes:
    1. Boundary Violation (境界侵害)
    2. Uncontrollability (制御不能性)
    3. Anticipated Loss (予期的喪失)
    """

    # 3-axis scores (0–10)
    boundary_violation: int = Field(ge=0, le=10, description="境界侵害スコア")
    uncontrollability: int = Field(ge=0, le=10, description="制御不能性スコア")
    anticipated_loss: int = Field(ge=0, le=10, description="予期的喪失スコア")

    # Derived metadata
    dominant_axis: str = Field(description="最も強い軸")
    dominant_pattern: str = Field(description="支配的パターン（複合含む）")
    summary: str = Field(description="不安構造の要約")

    # Response control
    response_policy: ResponsePolicy

    # Factors
    controllable_factors: list[str] = Field(default_factory=list, description="制御可能な要素")
    uncontrollable_factors: list[str] = Field(default_factory=list, description="制御不能な要素")
    non_intervention_candidates: list[str] = Field(default_factory=list, description="NI候補")

    # Action guidance
    minimal_action_today: str = Field(description="今日の最小行動")
    stability_policy: str = Field(description="安定性方針")
    safety_note: str = Field(default="", description="安全に関する注意")

    @field_validator("boundary_violation", "uncontrollability", "anticipated_loss", mode="before")
    @classmethod
    def clamp_score(cls, v: int) -> int:
        """Ensure score stays within 0–10 range."""
        return max(0, min(10, int(v)))

    @property
    def total_load(self) -> int:
        """Sum of all 3 axes as overall load indicator."""
        return self.boundary_violation + self.uncontrollability + self.anticipated_loss

    @property
    def is_high_load(self) -> bool:
        """True if all 3 axes are significantly elevated (≥7 each or total ≥21)."""
        return (
            self.boundary_violation >= 7
            and self.uncontrollability >= 7
            and self.anticipated_loss >= 7
        ) or self.total_load >= 21

    def to_scores_dict(self) -> dict[str, int]:
        return {
            "boundary_violation": self.boundary_violation,
            "uncontrollability": self.uncontrollability,
            "anticipated_loss": self.anticipated_loss,
        }
