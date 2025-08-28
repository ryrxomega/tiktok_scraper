from pathlib import Path
from unittest.mock import MagicMock

from tiktok_downloader.domains.config.services import ConfigService
from tiktok_downloader.domains.config.repository import ConfigRepository
from tiktok_downloader.domains.config.schemas import Config


def test_load_config():
    """
    GIVEN a path
    WHEN the load_config method is called
    THEN it should call the repository's load_from_path method and return the result.
    """
    # ARRANGE
    mock_repo = MagicMock(spec=ConfigRepository)
    expected_config = Config(min_likes=100)
    mock_repo.load_from_path.return_value = expected_config

    config_service = ConfigService(repository=mock_repo)
    test_path = Path("fake/path/config.ini")

    # ACT
    result_config = config_service.load_config(test_path)

    # ASSERT
    # Verify that the service delegated the call to the repository
    mock_repo.load_from_path.assert_called_once_with(test_path)
    # Verify that the service returned the value from the repository
    assert result_config == expected_config
    assert result_config.min_likes == 100
