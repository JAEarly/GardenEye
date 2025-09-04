from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from detection.frame_diff import compute_movement_score


@pytest.fixture
def mock_video_file() -> Path:
    """Create a mock video file path."""
    return Path("/fake/video.MP4")


@patch("detection.frame_diff.cv2.VideoCapture")
@patch("detection.frame_diff.cv2.VideoWriter")
@patch("detection.frame_diff.subprocess.run")
def test__compute_movement_score__returns_valid_score(
    mock_subprocess: MagicMock, mock_video_writer: MagicMock, mock_video_capture: MagicMock, mock_video_file: Path
) -> None:
    """Test basic movement score computation."""
    # Mock video capture
    mock_cap = MagicMock()
    mock_video_capture.return_value = mock_cap
    mock_cap.get.side_effect = lambda prop: {
        mock_cap.get.call_count: 30,  # FPS
        mock_cap.get.call_count + 1: 1920,  # Width
        mock_cap.get.call_count + 2: 1080,  # Height
    }.get(mock_cap.get.call_count, 0)

    # Mock frames - simulate 3 frames
    frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
    frame2 = np.ones((1080, 1920, 3), dtype=np.uint8) * 50
    frame3 = np.ones((1080, 1920, 3), dtype=np.uint8) * 100

    mock_cap.read.side_effect = [
        (True, frame1),
        (True, frame2),
        (True, frame3),
        (False, None),  # End of video
    ]

    # Mock video writer
    mock_writer = MagicMock()
    mock_video_writer.return_value = mock_writer
    mock_writer.isOpened.return_value = True

    # Run the function
    score = compute_movement_score(mock_video_file)

    # Verify it returns a float score
    assert isinstance(score, float)
    assert 0 <= score <= 1

    # Verify video writer was called
    assert mock_writer.write.call_count == 3  # 3 frames written
    mock_writer.release.assert_called_once()
    mock_cap.release.assert_called_once()

    # Verify subprocess (ffmpeg) was called
    mock_subprocess.assert_called_once()


@patch("detection.frame_diff.cv2.VideoCapture")
def test__compute_movement_score__handles_no_frames(mock_video_capture: MagicMock, mock_video_file: Path) -> None:
    """Test handling of video with no readable frames."""
    mock_cap = MagicMock()
    mock_video_capture.return_value = mock_cap
    mock_cap.get.return_value = 30  # Mock basic properties
    mock_cap.read.return_value = (False, None)  # No frames

    with patch("detection.frame_diff.cv2.VideoWriter") as mock_writer_class:
        mock_writer = MagicMock()
        mock_writer_class.return_value = mock_writer
        mock_writer.isOpened.return_value = True

        with patch("detection.frame_diff.subprocess.run"):
            score = compute_movement_score(mock_video_file)
            # Should return NaN or 0 for empty frame list
            assert score == 0.0 or np.isnan(score)


@patch("detection.frame_diff.cv2.VideoWriter")
def test__compute_movement_score__raises_error_when_writer_fails(
    mock_video_writer_class: MagicMock, mock_video_file: Path
) -> None:
    """Test handling when video writer fails to open."""
    mock_writer = MagicMock()
    mock_video_writer_class.return_value = mock_writer
    mock_writer.isOpened.return_value = False

    with patch("detection.frame_diff.cv2.VideoCapture"):
        with pytest.raises(RuntimeError, match="Could not open video writer"):
            compute_movement_score(mock_video_file)
