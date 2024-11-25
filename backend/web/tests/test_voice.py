import pytest
import edge_tts
import httpx
import os
import tempfile
from ..tts import tts
from ..config import get_settings

pytest_plugins = ("pytest_asyncio",)

FISH_API = "http://localhost:8080"


@pytest.mark.asyncio
async def _test_fish_api():
    client = httpx.Client()
    format = 'wav'
    data = {
        "text": "你好，我是客服小祥，有什么可以帮忙的吗？今天天气不错啊",
        "chunk_length": 300,
        "format": format,
        "mp3_bitrate": 64,
        "references": [],
        "reference_id": "sakiko",
        "seed": None,
        "use_memory_cache": "never",
        "normalize": True,
        "opus_bitrate": -1000,
        "latency": "normal",
        "streaming": False,
        "max_new_tokens": 2048,
        "top_p": 0.7,
        "repetition_penalty": 1.2,
        "temperature": 0.7,
    }
    resp = client.post(f"{FISH_API}/v1/tts", json=data)
    with tempfile.NamedTemporaryFile(prefix="test_voice-", suffix=f".{format}") as fp:
        fp.write(resp.content)
        fp.flush()

        os.system(f"file {fp.name}")
        os.system(f"play {fp.name}")


@pytest.mark.asyncio
async def _test_edge_tts():
    """ """
    TEXT = "你好，我是客服小祥，有什么可以帮忙的吗"
    # all female chinese voices by edge-tts
    VOICE_LIST = [
        "zh-CN-XiaoyiNeural",
        "zh-CN-liaoning-XiaobeiNeural",
        "zh-CN-shaanxi-XiaoniNeural",
        "zh-HK-HiuGaaiNeural",
        "zh-HK-HiuMaanNeural",
        "zh-TW-HsiaoChenNeural",
        "zh-TW-HsiaoYuNeural",
    ]
    VOICE = VOICE_LIST[0]
    communicate = edge_tts.Communicate(TEXT, VOICE, rate="+50%")
    
    with tempfile.NamedTemporaryFile(prefix="test_voice-", suffix=".mp3") as fp:
        async for chunk in communicate.stream():
            # print(chunk)
            if chunk['type'] == 'audio':
                fp.write(chunk['data'])
        fp.flush()

        print(VOICE)
        os.system(f"file {fp.name}")
        os.system(f"play {fp.name}")



@pytest.mark.asyncio
async def test_tts_module():
    voice_preset = get_settings().bot_preset.get('sakiko').voice
    print(voice_preset)
    voice_buf = await tts("你好，我是客服小祥", voice_preset)
    print(voice_buf)
    
    with tempfile.NamedTemporaryFile(prefix="test_voice-", suffix=".mp3") as fp:
        fp.write(voice_buf)
        fp.flush()
        os.system(f"file {fp.name}")
        os.system(f"play {fp.name}")
