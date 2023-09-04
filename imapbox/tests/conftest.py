import pytest
from imapbox import MailBox
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str
    port: int
    user: str
    password: str

    model_config = SettingsConfigDict(env_file='imapbox/tests/.env')


settings = Settings()


@pytest.fixture(scope='session')
def mail_box():
    print(settings.host)
    box = MailBox(settings.host, settings.port)
    box.login(settings.user, settings.password)
    yield box
    box.quit()
