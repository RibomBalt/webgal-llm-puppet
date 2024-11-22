from pydantic import BaseModel, constr
from ..logger import model_logger
import random

class BotSecret(BaseModel):
    model: str = "mockai"
    api_key: str = "sk-"
    base_url: str = "http://localhost:5002/v1"


class BotParams(BaseModel):
    """parameters to pass into bots"""

    temperature: float = 1.5
    presence_penalty: float = 1.0


class BotPreset(BaseModel):
    """Common for all LLM bots"""

    llm_name: str
    speaker: str
    system_prompt: str = ""
    welcome_message: str = ""
    llm_params: BotParams = BotParams()


# class L2dAction(BaseModel):
#     motion: str
#     expression: str


class L2dBotPreset(BotPreset):
    """Bot with L2D, and controls of mood"""

    live2d_model_path: str
    mood: dict[str, list[constr(pattern="^[a-zA-Z0-9]+?\\:[a-zA-Z0-9]+?$")]]
    bye_message: str = ""

    def random_motion(self, test_mood: str = None):
        """choose a set of motion (motion:expression to be exact)
        """
        if test_mood not in self.mood:
            _test_mood = test_mood
            test_mood = random.choice(list(self.mood.keys()))
            model_logger.warning(f"unrecognized mood {_test_mood}, choose random one: {test_mood}")

        return random.choice(self.mood[test_mood])
