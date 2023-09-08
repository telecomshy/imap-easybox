import pytest
from imaplib import IMAP4_SSL
from imapbox import ImapBox
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    user: str
    password: str

    model_config = SettingsConfigDict(env_file='imapbox/tests/test_126_box/.env', env_file_encoding='utf-8')


settings = Settings()


@pytest.fixture(scope='session')
def mail_box():
    box = ImapBox(settings.host, settings.port, settings.user, settings.password)
    box.login()
    yield box
    box.quit()
