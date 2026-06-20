import os
import sys
from unittest.mock import patch

import pytest

from src import spark_pipeline


def test_validate_runtime_environment_rejects_unsupported_python() -> None:
    with patch.object(spark_pipeline.sys, "version_info", (3, 14, 0)):
        with pytest.raises(SystemExit, match="Python 3.11"):
            spark_pipeline.validate_runtime_environment()


def test_validate_runtime_environment_rejects_missing_java() -> None:
    with patch.object(spark_pipeline.sys, "version_info", (3, 11, 0)):
        with patch.object(spark_pipeline.shutil, "which", return_value=None):
            with pytest.raises(SystemExit, match="OpenJDK 17"):
                spark_pipeline.validate_runtime_environment()


def test_validate_runtime_environment_allows_java_without_java_home(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(spark_pipeline.sys, "version_info", (3, 11, 0)):
        with patch.object(spark_pipeline.shutil, "which", return_value="/usr/bin/java"):
            with patch.dict(os.environ, {}, clear=True):
                spark_pipeline.validate_runtime_environment()

    captured = capsys.readouterr()
    assert "JAVA_HOME is not set" in captured.err
