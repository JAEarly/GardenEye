from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request

from garden_eye.api.range_stream import _parse_range, range_file_response


def test__parse_range__valid_start_end() -> None:
    """Test parsing range header with start and end."""
    start, end = _parse_range("bytes=0-499", 1000)
    assert start == 0
    assert end == 499


def test__parse_range__start_only() -> None:
    """Test parsing range header with start only."""
    start, end = _parse_range("bytes=500-", 1000)
    assert start == 500
    assert end == 999


def test__parse_range__suffix_range() -> None:
    """Test parsing range header with suffix."""
    start, end = _parse_range("bytes=-200", 1000)
    assert start == 800
    assert end == 999


def test__parse_range__suffix_larger_than_file() -> None:
    """Test parsing range header with suffix larger than file."""
    start, end = _parse_range("bytes=-2000", 1000)
    assert start == 0
    assert end == 999


def test__parse_range__invalid_header_format() -> None:
    """Test parsing invalid range header format."""
    with pytest.raises(HTTPException) as exc_info:
        _parse_range("invalid", 1000)
    assert exc_info.value.status_code == 416
    assert "Invalid Range header" in exc_info.value.detail


def test__parse_range__invalid_units() -> None:
    """Test parsing range header with invalid units."""
    with pytest.raises(HTTPException) as exc_info:
        _parse_range("items=0-499", 1000)
    assert exc_info.value.status_code == 416
    assert "Only 'bytes' range supported" in exc_info.value.detail


def test__parse_range__invalid_range_format() -> None:
    """Test parsing range header with invalid range format."""
    with pytest.raises(HTTPException) as exc_info:
        _parse_range("bytes=0-499-999", 1000)
    assert exc_info.value.status_code == 416
    assert "Invalid range format" in exc_info.value.detail


def test__parse_range__zero_suffix() -> None:
    """Test parsing range header with zero suffix."""
    with pytest.raises(HTTPException) as exc_info:
        _parse_range("bytes=-0", 1000)
    assert exc_info.value.status_code == 416
    assert "Invalid suffix length" in exc_info.value.detail


def test__parse_range__invalid_bounds() -> None:
    """Test parsing range header with invalid bounds."""
    with pytest.raises(HTTPException) as exc_info:
        _parse_range("bytes=500-499", 1000)
    assert exc_info.value.status_code == 416
    assert "Invalid range bounds" in exc_info.value.detail


def test__parse_range__negative_start() -> None:
    """Test parsing range header with negative start."""
    # This is actually a valid suffix range (-10) followed by invalid format (10-499)
    # The current implementation will fail on int("10-499")
    with pytest.raises(ValueError):
        _parse_range("bytes=-10-499", 1000)


def test__range_file_response__file_not_found() -> None:
    """Test range_file_response with non-existent file."""
    mock_request = MagicMock(spec=Request)
    non_existent_file = Path("/non/existent/file.mp4")

    with pytest.raises(HTTPException) as exc_info:
        range_file_response(non_existent_file, mock_request)
    assert exc_info.value.status_code == 404
    assert "File not found" in exc_info.value.detail


def test__range_file_response__with_range_header(tmp_path: Path) -> None:
    """Test range_file_response with range header."""
    # Create a test file
    test_file = tmp_path / "test.mp4"
    test_content = b"0123456789" * 100  # 1000 bytes
    test_file.write_bytes(test_content)

    # Mock request with range header
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.side_effect = lambda key: "bytes=0-499" if key in ["range", "Range"] else None

    response = range_file_response(test_file, mock_request)

    # Verify response
    assert response.status_code == 206
    assert response.media_type == "video/mp4"
    assert "Content-Range" in response.headers
    assert response.headers["Content-Range"] == "bytes 0-499/1000"
    assert response.headers["Content-Length"] == "500"


def test__range_file_response__without_range_header(tmp_path: Path) -> None:
    """Test range_file_response without range header."""
    # Create a test file
    test_file = tmp_path / "test.mp4"
    test_content = b"0123456789" * 100  # 1000 bytes
    test_file.write_bytes(test_content)

    # Mock request without range header
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.return_value = None

    response = range_file_response(test_file, mock_request)

    # Verify response
    assert response.status_code == 200
    assert response.media_type == "video/mp4"
    assert "Content-Length" in response.headers
    assert response.headers["Content-Length"] == "1000"
    assert response.headers["Accept-Ranges"] == "bytes"


def test__range_file_response__case_insensitive_range_header(tmp_path: Path) -> None:
    """Test range_file_response with case-insensitive Range header."""
    # Create a test file
    test_file = tmp_path / "test.mp4"
    test_content = b"0123456789" * 100  # 1000 bytes
    test_file.write_bytes(test_content)

    # Mock request with Range (capital R) header
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.side_effect = lambda key: "bytes=100-199" if key == "Range" else None

    response = range_file_response(test_file, mock_request)

    # Verify response
    assert response.status_code == 206
    assert response.headers["Content-Range"] == "bytes 100-199/1000"


def test__range_file_response__end_beyond_file_size(tmp_path: Path) -> None:
    """Test range_file_response handles end position beyond file size."""
    # Create a test file
    test_file = tmp_path / "test.mp4"
    test_content = b"0123456789" * 10  # 100 bytes
    test_file.write_bytes(test_content)

    # Mock request with range header that goes beyond file size
    mock_request = MagicMock(spec=Request)
    mock_request.headers.get.side_effect = lambda key: "bytes=50-200" if key in ["range", "Range"] else None

    response = range_file_response(test_file, mock_request)

    # Verify response - end should be clamped to file size
    assert response.status_code == 206
    assert response.headers["Content-Range"] == "bytes 50-99/100"
    assert response.headers["Content-Length"] == "50"
