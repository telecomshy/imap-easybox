import pytest
from imap_easybox import ImapEasyBox
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    user: str
    password: str

    model_config = SettingsConfigDict(env_file='./tests/test_126_box/.env', env_file_encoding='utf-8')


settings = Settings()


@pytest.fixture(scope='session')
def mail_box():
    box = ImapEasyBox(settings.host, settings.port, settings.user, settings.password)
    box.login()
    yield box
    box.quit()


@pytest.fixture(scope='session')
def inbox(mail_box):
    inbox = mail_box.select('inbox')
    return inbox
