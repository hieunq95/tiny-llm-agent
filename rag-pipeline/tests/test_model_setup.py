import os
import pytest
from unittest.mock import patch, MagicMock
from model_setup import load_model

@pytest.fixture
def mock_dependencies(mocker):
    """Mock dependencies to avoid real downloads and model loading."""
    # Mock get_hardware
    mocker.patch("model_setup.get_hardware", return_value="cpu")

    # Mock snapshot_download to prevent real downloading
    mock_snapshot = mocker.patch("model_setup.snapshot_download")

    # Mock AutoModelForCausalLM.from_pretrained to prevent real model loading
    mock_model = MagicMock()
    mock_load = mocker.patch("model_setup.AutoModelForCausalLM.from_pretrained", return_value=mock_model)

    return mock_snapshot, mock_load

def test_load_model_existing(mock_dependencies, tmp_path):
    """Test when the model already exists locally."""
    mock_snapshot, mock_load = mock_dependencies
    local_dir = tmp_path / "model"
    os.makedirs(local_dir, exist_ok=True)

    # Create a dummy config file to simulate an existing model
    (local_dir / "config.json").write_text("{}")

    model = load_model("dummy_model", str(local_dir))

    # Ensure snapshot_download was NOT called
    mock_snapshot.assert_not_called()

    # Ensure the model is loaded
    mock_load.assert_called_once_with(pretrained_model_name_or_path=str(local_dir), device_map="cpu")
    assert model is not None

def test_load_model_not_existing(mock_dependencies, tmp_path):
    """Test when the model does not exist locally and needs to be downloaded."""
    mock_snapshot, mock_load = mock_dependencies
    local_dir = tmp_path / "model"

    model = load_model("dummy_model", str(local_dir))

    # Ensure snapshot_download was called
    mock_snapshot.assert_called_once_with(repo_id="dummy_model", local_dir=str(local_dir))

    # Ensure the model is loaded
    mock_load.assert_called_once_with(pretrained_model_name_or_path=str(local_dir), device_map="cpu")
    assert model is not None
