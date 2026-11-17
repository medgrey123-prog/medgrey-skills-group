# 模板

- `cinematic-light/`：已确认的科学风格「光之剧场」。`film.html` 是可运行的《叶子为什么是绿的》成片模板，文案集中在顶部的 `LESSON`。需要同目录的 `common.js` 和 `L/build/timings.json`。
- `watercolor-book/`：已确认的情绪风格「水彩绘本」。`film.html` 是可运行的《生气的时候怎么办》成片模板。需要 `common.js`、`emo.js`、`L/build/timings.json`。可选把 LXGW WenKai 放到 `fonts/wenkai.ttf`。
- `style-frames/`：风格确认用的单帧页（科学 6 种、情绪 6 种）。用 `scripts/shoot.py --root templates/style-frames --html <文件>` 截图。

换知识点时，用 `scripts/init_project.py` 把整套模板拷到工作目录再改，不要直接在 templates 里覆盖。
