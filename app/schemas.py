from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# RULE SCHEMAS
# ============================================================

class RuleCreate(BaseModel):
    keyword: str
    dm_message: str


class RuleResponse(BaseModel):
    rule_id: str
    keyword: str
    dm_message: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# STATS SCHEMA
# ============================================================

class StatsResponse(BaseModel):
    sent: int
    failed: int
    queued: int
    duplicates_blocked: int


# ============================================================
# EVENT RESPONSE
# ============================================================

class EventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# JOB RESPONSE
# ============================================================

class JobResponse(BaseModel):
    id: int
    user_id: str
    rule_id: int
    comment_id: str
    message: str
    status: str
    retry_count: int
    dm_id: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# WEBHOOK USER
# ============================================================

class WebhookUser(BaseModel):
    user_id: str
    username: Optional[str] = None


# ============================================================
# WEBHOOK DATA
# ============================================================

class WebhookData(BaseModel):
    comment_id: Optional[str] = None
    post_id: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[str] = None

    # JSON uses "from", but Python cannot use "from"
    from_: Optional[WebhookUser] = Field(
        default=None,
        alias="from"
    )

    model_config = ConfigDict(
        populate_by_name=True
    )


# ============================================================
# WEBHOOK EVENT
# ============================================================

class WebhookEvent(BaseModel):
    event_id: str
    event_type: str
    sent_at: Optional[str] = None
    data: WebhookData