from app.config import get_settings


def test_settings_read_env(temp_store):
    presets, data = temp_store
    settings = get_settings()
    assert settings.presets_dir == presets
    assert settings.data_dir == data
    assert settings.brute_force_guard == 10
    assert settings.default_restarts == 20
