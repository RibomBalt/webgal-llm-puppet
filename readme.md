# 部署方式

## API KEY
1. 获取一个支持使用python openai库调用的API KEY（我用的deepseek）
2. 在`backend/secrets.yml`中，并按格式添加内容：
   1. 前面的名字：默认为`deepseek`，需要和`system_prompts.yml`中`sakiko - model`保持一致
   2. `model`: 模型内部名，是传入OpenAI客户端的名称，以deepseek为例，应该填`deepseek-chat`
   3. `api_key`: 你的KEY
   4. `base_url`: 你的模型URL

## 系统提示词 & 定制
提示词、模型参数和表情配置等默认保存`backend/system_prompts.yml`中，每一组是一个【预设】（对应到[源码](backend/web/models/bot.py)中即`BotPreset`或者`L2dBotPreset`类）

其他参数不说自明（懒得写了）。需要特别说明的参数：
- `mood`: 这个字典项，都是一个表情名称到多个l2d动作/表情代号的字典。表情代号除了`listening`是刚接受用户输入后使用，其他表情都是`mood_analyzer`这个预设的系统提示词返回的信息。程序对每句回复会请求`mood_analyzer`判断这一句的情感倾向，然后找到`mood`中对应项的列表，随机抽取一个作为这句话的动作/表情。

如果你需要加新的预设（比如用其他L2D，表情，提示词等），你可以：

1. 把原本`sakiko`的预设复制一组，并填入内容
2. 在WebGAL的`start.txt`中，给`changeScene`的URL加上`?bot={你的预设名字}`

## 其他环境变量
在`.env`中可以修改backend的配置。

- `DEBUG`: 设为1可以看到backend的详细日志。如果你需要反馈BUG，记得把这个设为1后附上程序的相关输出。
- `HOST`, `PORT`: backend绑定的地址端口。目前这两个参数用于生成WebGAL要访问backend的URL地址。
- `PROXY_URL`: 可选。访问大模型时可以给一个代理，比如`http://127.0.0.1:7890`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_NAMESPACE`(未使用), `REDIS_PASSWORD`: 可选。这几个参数可以让后端用redis缓存，如果没有设置或设置错误，会自动fallback到用一个全局变量字典缓存。

## backend
- 准备一个Python=3.11环境（其他版本没测试）
- 安装依赖：`cd backend && pip install -r requirements.txt`
- 运行：`cd backend && python app.py`或者`cd backend && uvicorn app:app --port=10228 --reload`。这个服务需要挂在后台。

## WebGAL
我的启动脚本`start.txt`：
```
choose:客服小祥📞:llm|README.MD:help;
label:llm
changeScene:http://localhost:10228/webgal/newchat.txt?bot=sakiko;
label:help
changeFigure:none
changeScene:http://localhost:10228/static/readme.txt
```

首先你需要一个包含了mygo立绘和L2D的WebGAL引擎源码。简单来说你需要把群里的`MyGO2.2`文件夹里的内容复制到`packages/webgal/public`，然后按照[官方文档](https://docs.openwebgal.com/live2D.html)的做法下载L2D运行库并注释掉相关代码。

在此基础上，我还对WebGAL源码做了一点魔改，所有改动详见[webgal.git.diff](webgal.git.diff)。主要包括两个部分：

- 禁用针对`http`资源的预加载功能
- 调整输入框的字体大小、样式等

> 注：两个改动都是可选的。目前的代码理论上不需要禁用http预加载也能正常工作。样式修改也是为了让输入框使用更舒服。

完成修改后，你可以：
- 在WebGAL目录下`yarn dev`拉起一个临时服务器，然后访问控制台弹出的链接。
- 或者先`yarn build`后，在`packages/webgal/dist`下找到编译后的静态网页，然后用任何可以部署静态服务器的方式部署（例如`python -m http.server 3000`，或者nginx, apache2等等）

如果使用`WebGAL Terre`，目录`public/games/{你的项目名}`对应的是`yarn build`之后存储静态网页的目录。不过可能魔改WebGAL代码会变得不方便。