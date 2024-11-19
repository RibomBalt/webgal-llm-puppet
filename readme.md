# 部署方式

## API KEY
1. 获取一个符合OPENAI格式的API KEY（我用的deepseek，理论上OpenAI家的模型也可以）
2. 将`secrets.template.json`复制到`secrets.json`，并按格式添加内容：
   1. 前面的名字：默认为`deepseek`，需要和`system_prompts.json`中`sakiko - model`保持一致
   2. `model`: 模型内部名，是传入OpenAI客户端的名称，以deepseek为例，应该填`deepseek-chat`
   3. `api_key`: 你的KEY
   4. `base_url`: 你的模型URL


## backend
- 准备一个Python=3.11环境（其他版本没测试）
- 安装依赖：`cd backend && pip install -r requirements.txt`
- 运行：`cd backend && python app.py`。这个服务需要挂在后台。

## WebGAL
我的启动脚本`start.txt`：
```
choose:客服小祥📞:llm|README.MD:help;
label:llm
changeScene:http://localhost:10228/webgal/newchat.txt;
label:help
changeFigure:none
changeScene:http://localhost:10228/static/readme.txt
```

首先你需要一个包含了mygo立绘和L2D的WebGAL引擎源码。简单来说你需要把群里的`MyGO2.2`文件夹里的内容复制到`packages/webgal/public`，然后按照[官方文档](https://docs.openwebgal.com/live2D.html)的做法下载L2D运行库并注释掉相关代码。

在此基础上，我还对WebGAL源码做了一点魔改，所有改动详见[webgal.git.diff](webgal.git.diff)。主要包括两个部分：

- 禁用针对`http`资源的预加载功能
- 调整输入框的字体大小、样式等

完成修改后，你可以在WebGAL目录下`yarn dev`拉起一个临时服务器，然后访问控制台弹出的链接。