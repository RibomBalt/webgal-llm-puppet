# 部署方式

## 大模型 API KEY
1. 获取一个支持使用python openai库调用的API KEY（我用的deepseek）
2. 在`backend/secrets.yml`中，并按格式添加内容：
   1. 前面的名字：默认为`deepseek`，需要和`system_prompts.yml`中`sakiko - model`保持一致
   2. `model`: 模型内部名，是传入OpenAI客户端的名称，以deepseek为例，应该填`deepseek-chat`
   3. `api_key`: 你的KEY
   4. `base_url`: 你的模型URL

!!! note 或者你有条件也可以本地部署大模型，让`base_url`指向对应URL即可。

## 本项目（fastapi后端）
- 准备一个Python=3.11环境（其他版本没测试）
- 安装依赖：`cd backend && pip install -r requirements.txt`
- 运行：`cd backend && python app.py`或者`cd backend && uvicorn app:app --port=10228 --reload`。这个服务需要挂在后台。

## WebGAL
!!! info 我的WebGAL版本：4.5.9

### 准备带MyGO素材 + L2D库的WebGAL环境
首先你需要一个包含了mygo立绘和L2D的[WebGAL引擎源码](https://github.com/OpenWebGAL/WebGAL)。如果你在WebGAL的MyGO二创群里，你可以把群文件的`MyGO2.2`文件夹里的内容复制到`packages/webgal/public`（或者你也可以选择<s>手动</s>写脚本从bestdori直接下载）。目前版本的常服祥子的L2D模型会位于`packages/webgal/public/game/figure/mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json`，其中路径中`figure`的后的部分和`system_prompt.yml`中`live2d_model_path`相同，可以自行修改。

之后你还需要按照[官方文档](https://docs.openwebgal.com/live2D.html)的指南下载L2D运行库并注释掉相关代码。

### （可选）WebGAL界面美化/魔改
在此基础上，我还使用了群里的仿Bestdori UI，可以直接放到放`packages/webgal/public/game/template`中。另外处理用户输入的`getUserInput`组件不能用`template`修改，我直接修改了部分组件源码，包括调整输入框的位置、字体，用`textarea`支持多行输入，以及加入`Ctrl+Enter`直接提交输入的快捷键。

所有改动详见[webgal.git.diff](webgal.git.diff)。你可以视情况接受这些改动。

### 编译/部署WebGAL
完成修改后，你可以：
- 在WebGAL目录下`yarn dev`拉起一个临时服务器，然后访问控制台弹出的链接。
- 或者先`yarn build`后，在`packages/webgal/dist`下找到编译后的静态网页，然后用任何可以部署静态服务器的方式部署（例如`python -m http.server 3000`，或者nginx, apache2等等）

### start.txt 入口场景
我的启动脚本`start.txt`：
```
choose:客服小祥📞:llm|README.MD:help;
label:llm
bgm:http://localhost:10228/static/assets/office/office-ambience.mp3
changeScene:http://localhost:10228/webgal/newchat.txt?bot=sakiko;
label:help
changeFigure:none
changeScene:http://localhost:10228/webgal/readme.txt
```

!!! note 假如你因为某种原因把后端和WebGAL放在两台机器上，比如在一个远程服务器上部署fastapi后端，然后在本机浏览器打开WebGAL网页，你需要注意把localhost改成后端所在机器的IP地址。这是因为Web GAL是个纯静态项目，所有的资源请求其实都是你本机的浏览器发出的。

# 修改配置

!!! note 修改配置后需要重新启动后端才能生效。重新启动后正在进行的对话聊天记录会消失，无法继续对话。

## 系统提示词 & 定制
提示词、模型参数和表情配置等默认保存`backend/system_prompts.yml`中，每一组是一个【预设】（对应到[源码](backend/web/models/bot.py)中即`BotPreset`或者`L2dBotPreset`类）

其他参数不说自明（懒得写了）。需要特别说明的参数：
- `mood`: 这个字典项，都是一个表情名称到多个l2d动作/表情代号的字典。表情代号除了`listening`是刚接受用户输入后使用，其他表情都是`mood_analyzer`这个预设的系统提示词返回的信息。程序对每句回复会请求`mood_analyzer`判断这一句的情感倾向，然后找到`mood`中对应项的列表，随机抽取一个作为这句话的动作/表情。
- `voice`: 可选的配音模块。
  - `type`值如果为`fish`，则使用[fish-speech](https://github.com/fishaudio/fish-speech)项目，此时`api`为以[HTTP API模式](https://speech.fish.audio/zh/inference/#http-api)启动的fish-speech后端的路径，`voice_line`会设定`reference_id`参数，你需要提前在`fish-speech`主目录下建立`references/<reference_id>`文件夹，并放入参考音频和对应label文件。
  - `type`值如果为`edge`，则使用`edge-tts`项目，即用于微软edge浏览器的TTS。声线不可定制，但是响应速度快且效果稳定。如果懒得配AI祥子配音的环境，这个是最好的替代方案。
  - `type`值如果为`mahiruoshi`，则使用Mahiruoshi老师用Bert-VITS2配置的[
BangDream-Bert-VITS2](https://huggingface.co/spaces/Mahiruoshi/BangDream-Bert-VITS2)的API，此时`voice_line`需指定为`祥子`，`api`会忽略。**不建议使用，响应速度慢+效果随机，不如本地配一个fish-speech**
  - `type`为其他值会禁用声音模块。

如果你需要加新的预设（比如用其他L2D，表情，提示词等），你可以：

1. 把原本`sakiko`的预设复制一组，并填入内容
2. 在WebGAL的`start.txt`中，给`changeScene`的URL加上`?bot={你的预设名字}`

## 其他环境变量
在`.env`中可以修改backend的部分配置。

- `DEBUG`: 设为1可以看到backend的详细日志。如果你需要反馈BUG，记得把这个设为1后附上程序的相关输出。
- `HOST`, `PORT`: backend绑定的地址端口。还用于生成WebGAL要访问backend的URL地址。
- `PROXY_URL`: 可选。访问大模型时可以给一个代理，比如`http://127.0.0.1:7890`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_NAMESPACE`(未使用), `REDIS_PASSWORD`: 可选。这几个参数可以让后端用redis缓存，如果没有设置或设置错误，会自动fallback到用一个全局变量字典缓存。

# 主要素材借物
- [WebGAL](https://github.com/OpenWebGAL/WebGAL)项目
- 祥子L2D模型、各种MyGO相关素材、部分UI等：来自WebGAL mygo分群，获取群号：[https://t.bilibili.com/988536317204758563](https://t.bilibili.com/988536317204758563)
- 大语言模型：[deepseek](https://www.deepseek.com/)
- 配音：主要使用[fish-speech](https://github.com/fishaudio/fish-speech)，参考音频来自[bestdori](https://bestdori.com/)

部分其他素材：
  - 办公室环境音：[https://freesound.org/people/Nightwatcher98/sounds/407292/](https://freesound.org/people/Nightwatcher98/sounds/407292/)