import httpx

try:
    import edge_tts
except ImportError:
    edge_tts = None
import io
from .config import get_settings
from .models.voice import VoicePreset
from .logger import bot_logger


async def fish_tts(text: str, voice_preset: VoicePreset):
    """request a sound from fish-speech api
    TODO: check status of fish api when initialization
    """
    settings = get_settings()
    # body template, most params are kept fixed
    data = {
        "text": text,
        "chunk_length": 600,
        "format": "mp3",
        "mp3_bitrate": 128,
        "references": [],
        "reference_id": voice_preset.voice_line,
        "seed": None,
        "use_memory_cache": "never",
        "normalize": True,
        "opus_bitrate": -1000,
        "latency": "normal",
        "streaming": False,
        "max_new_tokens": 4096,
        "top_p": 0.7,
        "repetition_penalty": 1.2,
        "temperature": 0.7,
    }

    proxy_url = settings.proxy_url if settings.proxy_url != "" else None
    async with httpx.AsyncClient(proxy=proxy_url) as client:
        resp = await client.post(f"{voice_preset.api}/v1/tts", json=data)

    return resp.content


async def online_mahiruoshi_api(text: str, speaker: str):
    URL = f"https://mahiruoshi-bert-vits2-api.hf.space/?text={text}&speaker={speaker}"

    settings = get_settings()

    bot_logger.debug(f"get voice from {URL}")
    proxy_url = settings.proxy_url if settings.proxy_url != "" else None
    async with httpx.AsyncClient(proxy=proxy_url, timeout=20) as client:
        resp = await client.get(URL)

        bot_logger.debug(f"get voice status: {resp.status_code}")

    return resp.content


async def edge_run_tts(text: str, voice_preset: VoicePreset):
    # TODO validate first
    voice_line = voice_preset.voice_line
    if not voice_line.startswith(("zh-", "jp-")):
        # basic check on tts voice name
        voice_line = "zh-CN-XiaoyiNeural"

    settings = get_settings()
    proxy_url = settings.proxy_url if settings.proxy_url != "" else None
    communicate = edge_tts.Communicate(text, voice_line, rate="+30%", pitch="-10Hz", proxy=proxy_url)
    voice_io = io.BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            voice_io.write(chunk["data"])
    voice_io.seek(0)
    return voice_io.read()


async def tts(text: str, voice_preset: VoicePreset):
    """ """
    try:
        if voice_preset.type == "fish":
            return await fish_tts(text, voice_preset)

        elif voice_preset.type == 'mahiruoshi':
            # use mahiruoshi's huggingface API
            return await online_mahiruoshi_api(text, voice_preset.voice_line)

        elif voice_preset.type == "edge":
            ""
            if edge_tts is not None:
                return await edge_run_tts(text, voice_preset)
            else:
                return None
        else:
            # other recognized type indicates disabled tts
            return None

    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as err:
        bot_logger.warning(f"TTS err encountered: {err}", exc_info=True)
        return None
