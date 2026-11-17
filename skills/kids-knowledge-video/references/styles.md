# 画面风格

先定风格，再渲成片。用户没确认单帧之前，不要跑完整 30 秒。

所有成片都是 **1080×1920 竖屏**，函数 `window.render(t)`，时间单位是秒，必须确定（同样的 t 得到同一帧）。共享工具在 `templates/*/common.js`：随机数、噪声、缓动、颗粒、可选的 App 底栏示意。

## 已确认的两套（可直接当工作模板）

### 光之剧场 `cinematic-light`

适合：**自然科学、光、空间、微观结构**。科学试片《叶子为什么是绿的》采用此风格。

- 深色剧场空间，主体是发光的光线、光谱、叶绿素，而不是扁平图标。
- 光要用叠加（lighter）和多层 bloom，灰尘粒子在光柱里漂。
- 字体：中文用 Noto Sans CJK SC，英文字幕/编号用 IBM Plex Mono。
- 色：黑底，白光，彩虹色散，叶绿体的青绿，暗部略青。
- 工作模板：`templates/cinematic-light/film.html`（顶部有 `LESSON` 文案对象）。
- 风格确认帧：`templates/style-frames/science-cinematic-light.html`（科学）、`emotion-cinematic-ember.html`（情绪变体，未作为情绪课最终项）。

预览：`assets/previews/cinematic-light.jpg`。

### 水彩绘本 `watercolor-book`

适合：**认识情绪、和朋友相处、遇到困难怎么办**。情绪试片《生气的时候怎么办》采用此风格。

- 暖纸色、纸纹、多层透明水彩、边缘略深，像一本被翻开的绘本，而不是 UI 卡片。
- 手写标注、铅笔线、翻页，比「闪光特效」更重要。
- 字体：标题偏向 Noto Serif CJK SC；手写感可用 LXGW WenKai（需自行放到 `fonts/wenkai.ttf`），没有时回退到 Noto Sans CJK SC。
- 工作模板：`templates/watercolor-book/film.html`（含 `LESSON`，依赖 `emo.js` 里的小孩轮廓和水彩铺色）。
- 风格确认帧：`templates/style-frames/emotion-watercolor-book.html`。

预览：`assets/previews/watercolor-book.jpg`。

已知要避免的问题（来自试片，改新课时应修）：人物不要只用一个正面静止姿势；火苗最大时不要顶出画面；成片尽量收到 30 秒。

## 风格确认怎么做

1. 先用 `templates/style-frames/` 里现成的单帧页，或把工作模板的 `LESSON` 改成新标题后，截 1–2 个关键时刻。
2. 把图给用户看，只问风格，先不讨论配乐。
3. 点头后再写完整 `render(t)`、再配乐。

```bash
python scripts/shoot.py --root templates/style-frames --html emotion-watercolor-book.html \
  frame --time 0 --out /tmp/style-watercolor.png
```

单帧页里的 `t` 大多是一个展示时刻（科学光之剧场的关键时刻大约在 4.6 秒）。加 `?ui=1` 可叠一层 App 底栏，用来看留白，成片默认不要带。

## 可选风格（尚未作为某类目的默认项）

这些单帧都在 `templates/style-frames/`，可以拿来做新的风格确认，但还没有完整 30 秒成片。

科学向：

| 文件 | 风格 | 大意 |
|---|---|---|
| science-museum-plate.html | 博物图版 | 纸、铜版刻线、手工着色，像博物馆图版 |
| science-flat-depth.html | 扁平纵深 | 分层矢量、轮廓光，偏科普动画 |
| science-glass-clay-3d.html | 玻璃与黏土 | 柔光立体、玻璃棱镜和色散 |
| science-keynote-minimal.html | 发布会极简 | 白舞台，一件主角，很少装饰 |
| science-papercut-diorama.html | 纸雕层叠 | 纸纹和多层阴影的立体书 |

情绪向：

| 文件 | 风格 | 大意 |
|---|---|---|
| emotion-cinematic-ember.html | 光之剧场·情绪 | 发光轮廓，怒火像火星，呼吸使其冷却 |
| emotion-papercut-diorama.html | 纸雕层叠·情绪 | 纸人、纸火焰 |
| emotion-colorfield-orb.html | 情绪色场 | 抽象色块从尖、热变为圆、冷 |
| emotion-riso-editorial.html | 孔版印刷 | 荧光粉 / 蓝 / 黄专色和网点 |
| emotion-soft-clay-3d.html | 柔光黏土 | 软黏土小孩捧着一小团火 |

不要同时把所有风格做成片。一次只确认一套，通过后再进入完整流程。

## 写新动画时的约定

- 画布必须是 `<canvas id="c" width="1080" height="1920">`。
- `window.render(t)` 可同步可返回 Promise；如需先加载时间轴，把 Promise 挂在 `window.ready` 上。
- 时间跟 `timings.json` 的 cue 走，不要把关键动作写死成「第 12 秒」后就不再改。旁白一重录，时间就会变。
- 相邻约 2 秒，画面上要有肉眼可见的变化。
- 不要默认为了「好看」去做和内容无关的淡入淡出。转场最好从内容里长出来（光带着镜头走，纸页翻过去）。
