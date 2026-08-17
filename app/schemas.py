from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


# =========================
# Rule Schemas
# =========================

class RuleCreate(BaseModel):
    keyword: str
    dm_message: str


class RuleResponse(BaseModel):
    rule_id: str
    keyword: str
    dm_message: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# Stats Schema
# =========================

class StatsResponse(BaseModel):
    sent: int
    failed: int
    queued: int
    duplicates_blocked: int


# =========================
# Event / Job Schemas
# =========================

class EventResponse(BaseModel):
    id: int
    event_id: str
    event_type: str

    model_config = ConfigDict(from_attributes=True)


class JobResponse(BaseModel):
    id: int
    user_id: str
    rule_id: int
    comment_id: str
    message: str
    status: str
    retry_count: int
    dm_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# =========================
# Webhook Schemas
# =========================

class WebhookUser(BaseModel):
    user_id: str
    username: Optional[str] = None


class WebhookData(BaseModel):
    comment_id: Optional[str] = None
    post_id: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[str] = None
    from_: Optional[WebhookUser] = Field(default=None, alias="from")

    model_config = ConfigDict(populate_by_name=True)


class WebhookEvent(BaseModel):
    event_id: str
    event_type: str
    sent_at: Optional[str] = None
    data: WebhookData
