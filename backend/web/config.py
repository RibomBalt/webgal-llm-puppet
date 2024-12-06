from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import cached_property, lru_cache
from yaml import safe_load as yaml_load
from .models.bot import BotSecret, BotPreset, L2dBotPreset
import os


class AppSettings(BaseSettings):
    debug: bool = False
    llm_secret: BotSecret = BotSecret()
    enable_mood: bool = True

    host: str = "127.0.0.1"
    port: int = 10228
    webgal_baseurl: str = "http://localhost:3000"
    proxy_url: str = ""
    # preset and secrets path
    llm_secret_yml: str = "secrets.yml:secrets.dev.yml"
    llm_preset_yml: str = "system_prompt.yml:system_prompt.dev.yml"
    # cache properties
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_namespace: str = "llm_webgal"
    redis_password: str = ""

    model_config = ConfigDict(env_file=(".env", "prod.env", "dev.env"))

    @cached_property
    def bot_preset(self) -> dict[str, BotPreset | L2dBotPreset]:
        """ """
        bot_presets = {}
        for preset_file_name in self.llm_preset_yml.split(":"):
            if not os.path.isfile(preset_file_name):
                continue

            with open(preset_file_name, "r", encoding="utf-8") as fp:
                sys_prompt_yml: dict = yaml_load(fp.read())
            for k, v in sys_prompt_yml.items():
                if "live2d_model_path" in v:
                    bot = L2dBotPreset.model_validate(v)
                else:
                    bot = BotPreset.model_validate(v)

                bot_presets[k] = bot

        return bot_presets

    @cached_property
    def secret_pool(self) -> dict[str, BotSecret]:
        """ """
        secrets = {}
        for secret_fname in self.llm_secret_yml.split(":"):
            if not os.path.isfile(secret_fname):
                continue
            
            with open(secret_fname, "r", encoding="utf-8") as fp:
                secrets_obj = yaml_load(fp.read())
            # shallow merge
            for k, v in secrets_obj.items():
                secrets[k] = BotSecret.model_validate(v)
        return secrets


@lru_cache
def get_settings():
    settings = AppSettings()
    return settings
