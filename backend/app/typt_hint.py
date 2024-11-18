from typing import Literal

Message = dict[Literal["role", "content"], str]
Secret = dict[Literal["model", "api_key", "base_url"], str]
Preset = dict[Literal["model", "speaker", "system_prompt", "welcome_message", "model_params"] | str, str | dict]
Mood = dict[str, list[str]]