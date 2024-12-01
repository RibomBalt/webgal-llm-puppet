{% raw %}changeBg:N（主角相关工作地点）/N9.jpg -next
; preload transparent figures
changeFigure:assetSetter.png -left -transform={"alpha":0,"position":{"x":-400},"scale":{"x":0.3,"y":0.3}} -next;
changeFigure:contentParser.png -right -transform={"alpha":0,"position":{"x":400},"scale":{"x":0.3,"y":0.3}} -next -id=contentParser;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -motion=idle01 -expression=idle01 -next;
;start scripts
:照着稿子念一遍，今天就可以下班了。
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=bye02 -expression=smile01 -next;
客服小祥:各位B站的朋友大家好。 -center
刚刚我所有的发言都是根据实时输入，用大语言模型实时生成的。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking02 -expression=smile01 -next;
下面我简单介绍一下实现原理。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=smile01 -next;
给没有用过WebGAL的朋友解释一下：WebGAL游戏的运行逻辑是由一系列被称为【场景文件】的脚本控制的。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile01 -expression=smile01 -next;
这包括了所有的文字和演出，比如立绘、动画、音效、以及分支跳转。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile01 -expression=smile02 -next;
自然，从一个场景文件也可以跳转到另一个场景文件，这样能方便把多个章节分开，方便管理。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile03 -expression=smile03 -next;
不过大家可能不知道的是，跳转的目标不仅可以是本地的另一个场景文件，也可以是一个链接，表示一个远程的资源或场景文件。 -center;

setTransform:{"alpha":1,"position":{"x":-500},"scale":{"x":0.5,"y":0.5},"position":{"y":-100}} -target=fig-left -next;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf_left01 -expression=smile03 -next;
源码里对绝对链接甚至有特殊处理。 -center;
setTransform:{"alpha":0,"scale":{"x":0.1,"y":0.1},"position":{"y":-100}} -target=fig-left -next;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=smile01 -next;
同时，这版WebGAL刚好提供了一个获取用户输入的功能，就像这样弹一个输入框 -next;
getUserInput:a

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf02 -expression=kime01 -next;
客服小祥:然后，就可以把输入嵌入到链接里，发送给我们提前架好的服务器，请求新的场景脚本。 -center
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf03 -expression=smile06 -next;
服务器拿到嵌入在链接中的输入，和大模型对话后，可以把回复转变成新的脚本，再在结尾加上下一次请求的场景跳转。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile04 -expression=smile01 -next;
这样整个系统就转起来了，事实上实现了和后端大模型的双向通信。|WebGAL变成了一个巨大的点播机，内容完全由一个外部的Web APP控制。 -center;

不过虽然这种从外部编程控制WebGAL的想法听起来很爽，仔细想想好像…… -center -notend;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile04 -expression=serious02 -next;
其实没什么用？ -concat -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad02 -expression=sad02 -next;
这套玩法最合适的应用就是LLM对话，除此外也可以当桌宠或者L2D弹幕姬。|不过不如用专属软件，WebGAL这种主动请求的架构也不适合做这个事。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile03 -expression=smile03 -next;
嘛……不过确实很好玩就是了，毕竟高强度溜二创的话， -center -notend;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile03 -expression=smile02 -next;
看见这框那冰的感觉就来了。 -concat -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf01 -expression=thinking01 -next;
具体实现方面，程序本体没有特别有趣，练手性质的FastAPI小项目，大家如果对某些实现感兴趣可以来读源码。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sigh02 -expression=sigh02 -next;
关于系统提示词，也就是给大模型介绍大祥老师人设的这一部分。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sigh02 -expression=sigh01 -next;
提示词改了很多版，目前这版塞了很多人设进去，|但是感觉召回率不高，也就是很多信息其实回复中体现不出来，就像没有记住一样。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad02 -expression=sad02 -next;
具体体现就是，经常感觉不到【丰川祥子】的专属特点，而是真的在和一个普通的【客服】对话。而且作为客服的素质疑似有些太高了。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=odoodo01 -next;
不过意外地特别喜欢爆典， -notend -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=angry06 -expression=angry06 -next;
“真是高高在上呢”和 -notend -concat -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=angry07 -expression=angry07 -next;
“软弱的我已经死了” -notend -concat -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=shame01 -expression=shame01 -next;
这两句召回率奇高，我估计是因为这两句泛用性极高，所以AI也喜欢用。 -concat -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=cry03 -expression=surprised02 -next;
另外这位大祥老师有点藏不住话，很多时候问什么答什么，经常主动破坏Ave Mujica的世界观。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=shame02 -expression=shame02 -next;
对C团众的态度也有点非常温柔，如果你以自己是C团众的身份对话，她甚至会愿意跟你好好说话。显然让她理解大祥老师的底层逻辑还是有点困难。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=shame02 -expression=smile05 -next;
当你谈到一些提示词没有的东西的时候还是会胡言乱语，典中典之大模型【我超幻觉来了】。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=odoodo01 -expression=cry01 -next;
综上所述，OOC是难以避免的，这点我确实没什么办法。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=serious02 -expression=serious02 -next;
另外特别声明，截止到发稿UP还没看到Ave Mujica第一集，所以提示词也是根据MyGO部分撰写的，还请各位暂时不要剧透我orz -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nod01 -expression=sigh01 -next;
当然，只有文字响应是远远不够的，不然干嘛不去用大模型的官方网页端呢。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=serious01 -expression=serious01 -next;
在我看来，MyGO假药之所以能这么上头，L2D加持下的细腻演出是非常重要的一环。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad02 -expression=sad02 -next;
当然作为一个AI动态生成内容的项目，显然不能像各位神仙老师们一样琢磨微调，跟【细腻】这两个字算是告别了。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad02 -expression=kime01 -next;
然而AI加持也有自己的优势，很多事情也可以直接交给大模型一把梭了。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=kime01 -expression=kime01 -next;
比如动作和表情，我们至少可以问问大模型，刚才这几句回复的喜怒哀乐情感基调是什么样的？ -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=kime01 -expression=smile02 -next;
我们可以提前预设好的几类情感对应的演出效果，从中随机抽取。|效果勉强合格吧，还有微调提升的空间。 -center;

bgm:soyo_chap8.mp3 -enter=24000;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf01 -expression=sigh01 -next;
语音方面，其实本来是没打算做AI小祥的语音的。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad01 -expression=sad01 -next;
本来只打算做个简单的大模型聊天bot，我也没想继续做的。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=surprised01 -expression=surprised01 -next;
但是，就是刷到了不少AI祥子说话或者唱歌的视频，我也实在是忍不住…… -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad01 -expression=sad01 -next;
抱歉，让大家受伤了吧（指给大家听似人配音）| -center -notend;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sad01 -expression=angry02 -next;
就算无法原谅也是理所当然的，毕竟擅自演奏了对大家来说很重要的声音…… -center -concat;
:你的下一句话是不是：用AI配音是你的自由 -event235-27-015.mp3 -volume=30;
bgm:none;
客服小祥:咳咳，回归正题。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile01 -expression=smile06 -next;
我目前尝试用了fish-speech这个项目进行音声合成，使用了部分手游提取配音作为参考音源（来自bestdori） -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=thinking01 -next;
尝试过原始模型， -center -notend;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking02 -expression=serious02 -next;
也尝试过带少量祥子语音微调之后的版本。 -center -concat;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=sigh02 -expression=sigh01 -next;
其实调出这个效果我已经尽力了，还有很多小毛病。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=sigh02 -next;
可能最大的问题是fish这个项目不用语种标注，不少中文字是按日语发音给出的，我也无法调整语速、情感方面的信息。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nod01 -expression=sigh01 -next;
另外，参考音频对结果的影响是巨大的。多次试验后，我发现黑祥语音包的一致性比较好。大家听到的是随机抽取了25段黑祥干声作为参考音频的结果。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf01 -expression=sigh01 -next;
这已经是我抽奖抽出来最好的成果了。毕竟我这里要抽奖只能部署前抽，真正进入对话后生成的音频必须一次成功，要求是稍微高一些的。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=sad01 -next;
此外加入AI配音的代价是，会加入额外的等待时间。因为场景文件是在配音文件获取完后返回的，以确保WebGAL执行到配音的语句时，配音已经生成并缓存好了。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf03 -expression=smile01 -next;
作为替代，我还尝试了微软TTS（edge-tts），可以配出非常完美的中文配音。| -center -notend;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf03 -expression=smile05 -next;
除了和声线大祥老师毫无关联以外没有任何问题。 -concat -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf05 -expression=smile03 -next;
可以作为备选，毕竟Windows电脑上微软TTS似乎只要装一个Python包就行了。|而fish-speech需要配一整套环境，下载好几个GB的模型数据。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile05 -expression=smile05 -next;
当然如果确实受不了也可以在直接关掉配音。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=bye02 -expression=smile01 -next;
这方面我完全是小白。如果大家在定制声线的TTS上有心得的话，请不吝赐教。|我有空了也许会试试GPT-SoVITS等别的项目。 -center;

; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf04 -expression=smile03 -next;
; 最后毕竟我们这算是程序花活，果然还得聊点技术话题。|毕竟花了这么久读了WebGAL源码，不写下来那不是白读了。 -center;

; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile05 -expression=smile01 -next;
; 我最初拿到WebGAL源码，其实就是想看看能不能整点花活。 -center;
; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=kime01 -expression=kime01 -next;
; 比如在WebGAL里集成其它系统，或者在其他系统里集成WebGAL，这样说不定能扩展一下二创的工具链。 -center;
; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=smile01 -next;
; 大概看了一遍源码之后，我了解到WebGAL的产物是纯静态页面，所有场景文件和素材都被原样打包进构建产物中。 -center;
; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf05 -expression=smile01 -next;
; 于是我开始着重读素材和场景加载的部分，看看能不能找到一些方便的接口。 -center;

; setTransform:{"alpha":1,"position":{"x":-500},"scale":{"x":0.5,"y":0.5},"position":{"y":-100}} -target=fig-left -next;
; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf_left01 -expression=smile03 -next;
; 这段assetSetter显然是一个突破口，我看到了请求外部资源和代码的可行性。 -center;
; setTransform:{"alpha":0,"scale":{"x":0.1,"y":0.1},"position":{"y":-100}} -target=fig-left -next;

; setTransform:{"alpha":1,"scale":{"x":0.5,"y":0.5},"position":{"x":600, "y":-1200}} -target=contentParser -next;
; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nf_right01 -expression=smile05 -next;
; 在三种能触发外部场景加载的命令中，choose会把URL在第一个冒号处截断。|倒也算不上BUG，毕竟除了我谁会用WebGAL加载外部文件。 -center;
; setTransform:{"alpha":0,"scale":{"x":0.1,"y":0.1},"position":{"y":100}} -target=contentParser -next;
; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf04 -expression=smile01 -next;
; 但很幸运地，changeScene和callScene并不会截断URL，可以正常跳转到外部场景。 -center;

; changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf05 -expression=smile01 -next;
; 接下来解决如何把数据带出来的问题。 -center;
; WebGAL有一个被称为变量的特性，可以进行基本数值运算和字符串动态赋值和拼接。
; 事实上，即使是changeScene里的字符串，也可以代入变量的值，因此算是解决了带出数据的问题。
; 然而，WebGAL存在一个预加载机制：当一个场景文件时，引擎会首先扫描其中包含的资源文件，并进行提前加载。
; 被加载的资源会保存在一个列表中，加入再次加载的资源和列表的资源重复，则不会加载。
; 这个机制在正常使用中不会有任何问题，但在我这里可能会导致用户输入之前就把请求发过来了。如果不能区分请求是否真的发生在用户输入之后，会很麻烦。
; 幸好，预加载的请求不会代入变量，请求是以原本的形式发出来的，因而可以区分。

; 这样WebGAL的显示内容就可以完全由后端的API服务控制了，其实很像服务端主动推送的实现原理，由客户端主动长连接获取服务端数据。
; 也因此这个项目的后端我写的特别舒服，因为前后端完全分离，我几乎不用管WebGAL内部任何细节，只要提供正确的WebGAL场景脚本和资源就可以了。

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf03 -expression=smile01 -next;
最后，为了让有能力的网友们玩上这个项目，我会把当前版本的代码开源，你应该可以在简介或评论区找到github链接。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf03 -expression=smile02 -next;
开源代码里不包含API Key，还请自备。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=smile01 -next;
因为我的后端直接调用了openai库，因此只能用和openai库兼容的模型，比如GPT系模型或者部分国内模型。或者有条件的话也可以用本地的？ -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=smile04 -expression=smile04 -next;
总之谢谢大家看到这里，欢迎大家来玩这个项目。|如果大家不嫌弃我的代码质量的话也欢迎拿去二次开发，MIT授权。 -center;
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf03 -expression=smile03 -next;
如果玩出了什么新花样记得@我，就这样。 -center;

changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=nnf03 -expression=serious01 -next;
……结工资吧？ -center;
:按token结吗？
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=thinking01 -expression=serious02 -next;
{% endraw %}
客服小祥:今天一共使用了{{total_token}}个token，如果按1M token 1500日元计算的话，|大概需要{{ '{0:.2f}'.format(total_token / 1e6 * 1500) }}日元。 -center;
{%raw%}
changeFigure:mygo_avemujica_v6/sakiko/341_casual-2023_rip/model.json -transform={"position":{"y":-250}} -animationFlag=on -motion=cry01 -expression=cry01 -next;
{% endraw %}
只能买{{ '{0:.3f}'.format(total_token / 1e6 * 1500 / 600)}}份猪扒饭呢 -center;
playVideo:mygo_ed.mp4
end;