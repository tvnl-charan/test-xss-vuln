"""Pydantic models for admin endpoints."""

from typing import Optional, List
from pydantic import BaseModel, Field


class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="New role to assign")


class WebhookConfig(BaseModel):
    url: str = Field(..., description="Webhook delivery URL")
    events: List[str] = Field(default=["*"], description="Event types to subscribe to")
    secret: Optional[str] = Field(None, description="Optional signing secret override")


class BackupRequest(BaseModel):
    destination: str = Field("backups", description="Backup directory name")
    include_uploads: bool = Field(False, description="Whether to include uploaded files")


class AnalyticsExportRequest(BaseModel):
    format: str = Field("csv", description="Export format: csv or json")
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    include_pii: bool = Field(False, description="Whether to include PII fields")
