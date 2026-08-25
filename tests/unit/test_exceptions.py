"""Unit tests for Custom Exceptions and Error Codes."""

import pytest
from app.core.exceptions import (
    ConfigurationError,
    FeatureDisabledError,
    PipelineExecutionError,
    MuddyHTTPException,
)
from app.config.constants import ErrorCode


def test_custom_domain_exceptions():
    err = ConfigurationError("Missing key", details={"key": "SECRET"})
    assert err.code == ErrorCode.CONFIGURATION_ERROR
    assert err.details["key"] == "SECRET"

    feat_err = FeatureDisabledError("RAY_COMPUTE")
    assert feat_err.code == ErrorCode.FEATURE_DISABLED
    assert "RAY_COMPUTE" in str(feat_err)

    pipe_err = PipelineExecutionError("Step failed", step_name="Step2")
    assert pipe_err.code == ErrorCode.PIPELINE_ERROR
    assert pipe_err.details["failed_step"] == "Step2"


def test_muddy_http_exception():
    http_exc = MuddyHTTPException(status_code=400, detail="Invalid parameter", code=ErrorCode.VALIDATION_ERROR)
    assert http_exc.status_code == 400
    assert http_exc.detail["code"] == "VALIDATION_ERROR"
