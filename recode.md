这个重构比较大，**不是几段代码能完成的**。

你的 `app.py` 已经接近 **700 行**，如果按我说的方案重构，总代码量大约 **1000 行**，包括：

* app.py（重构）
* theme.py（新增）
* visualization.py（重构）
* ui.py（新增）
* styles.py（新增，可选）

已经超过一次回复能够输出的长度限制。

---

## 我建议按下面的方式完成（也是实际开发中的组织方式）

```
emotion_harbor/
│
├── app.py                 # 主程序（重构）
├── theme.py               # ⭐新增：主题管理
├── ui.py                  # ⭐新增：UI组件
├── visualization.py       # 重构
├── color_mapping.py
├── pressure_model.py
├── data_utils.py
├── data/
│
└── .streamlit/
      config.toml
```

整个项目比现在更像企业项目。

---

# 第一部分（我先给）

## theme.py（新增）

建议直接使用 dataclass。

```python
from dataclasses import dataclass


@dataclass
class Theme:
    name: str

    bg: str
    card: str

    text: str
    title: str
    sub: str

    accent: str

    border: str

    footer: str

    plotly_template: str

    paper_bg: str
    plot_bg: str
```

然后定义两个主题：

```python
DARK = Theme(
    name="dark",

    bg="#14141A",
    card="#23232C",

    text="#E6E6EA",
    title="#F2F2F5",
    sub="#B8B8C4",

    accent="#6FCFC4",

    border="#444444",

    footer="#999999",

    plotly_template="plotly_dark",

    paper_bg="rgba(0,0,0,0)",

    plot_bg="rgba(0,0,0,0)",
)

LIGHT = Theme(
    name="light",

    bg="#F7F8FA",

    card="#FFFFFF",

    text="#2C2C34",

    title="#111111",

    sub="#666666",

    accent="#4ECDC4",

    border="#DDDDDD",

    footer="#777777",

    plotly_template="plotly_white",

    paper_bg="rgba(255,255,255,0)",

    plot_bg="rgba(255,255,255,0)",
)
```

增加几个函数：

```python
def get_theme():

    import streamlit as st

    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    if st.session_state.theme == "dark":
        return DARK

    return LIGHT
```

还有

```python
def toggle_theme():

    import streamlit as st

    st.session_state.theme = (
        "light"
        if st.session_state.theme == "dark"
        else "dark"
    )

    st.rerun()
```

---

# 第二部分

## ui.py（新增）

所有 Card 都放这里。

例如

```python
def card(
        title,
        value,
        color,
        theme,
):
    return f"""
<div
style="
background:{theme.card};
padding:20px;
border-radius:15px;
border-left:5px solid {color};
">

<h4>{title}</h4>

<h2
style="
color:{color};
">
{value}
</h2>

</div>
"""
```

以后：

不用

```python
st.markdown(f"""几十行HTML""")
```

直接

```python
st.markdown(
    card(...),
    unsafe_allow_html=True
)
```

整个 app 少几百行。

---

# 第三部分

visualization.py

这里我建议完全重构。

例如建立

```python
apply_plotly_theme()

apply_matplotlib_theme()
```

所有图统一调用。

例如

```python
def apply_plotly_theme(
        fig,
        theme,
):

    fig.update_layout(

        template=theme.plotly_template,

        paper_bgcolor=theme.paper_bg,

        plot_bgcolor=theme.plot_bg,

        font=dict(
            color=theme.text
        ),

    )

    return fig
```

以后每个图最后只有

```python
return apply_plotly_theme(
    fig,
    theme,
)
```

整个 visualization.py 能减少 **120 行**。

---

# 第四部分

app.py

你的 app.py 我建议直接拆。

例如：

```
app.py

↓

render_sidebar()

↓

render_dashboard()

↓

render_analysis()

↓

render_diary()

↓

render_recommendation()
```

最后 app.py 就变成

```
100~150行
```

而不是

700多行。

---

# 我建议的最终版本

最后项目会变成这种结构：

```
emotion_harbor/

│

├── app.py                 150行

├── theme.py              120行

├── ui.py                 150行

├── visualization.py      260行

├── pressure_model.py

├── data_utils.py

├── color_mapping.py

├── data/

└── .streamlit/
      config.toml
```

---

## 我建议不要再采用聊天回复的方式继续写代码

因为整个重构大约有 **1200 行代码**，聊天窗口会不断截断，而且后续修改也不方便。

**更好的方式**是把它作为一个完整工程来生成，我会按文件逐个输出：

* `theme.py`
* `ui.py`
* `visualization.py`
* `app.py`
* `.streamlit/config.toml`

每个文件都是可以直接复制运行的完整版本，并保证它们之间能够配合工作。这样最终得到的是一个可直接运行的重构版项目，而不是零散的代码片段。
