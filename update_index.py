import os
import json
import subprocess
import urllib.parse
import re
import html
from datetime import datetime
from zoneinfo import ZoneInfo

import markdown


# ============================================================
# 基础配置
# ============================================================

POSTS_DIR = "posts"

BASE_URL = "https://syc-sigma.vercel.app"

LIST_FILE = "list.json"

# 统一只使用 sitemap.xml
SITEMAP_FILE = "sitemap.xml"

ROBOTS_FILE = "robots.txt"

ROUTE_PREFIX = "p"

TIME_CACHE_FILE = ".post_timestamps.json"

# 静态文章生成目录
ARTICLES_DIR = "articles"

# 时区
TZ = ZoneInfo("Asia/Shanghai")


# ============================================================
# Git 首次提交时间
# ============================================================

def get_first_git_timestamp(file_path):
    """
    获取某个 Markdown 文件第一次被 Git 提交的时间。

    返回：
        int: Unix timestamp
        None: 获取失败
    """

    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "--follow",
                "--diff-filter=A",
                "--format=%ct",
                "--reverse",
                "--",
                file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )

        output = result.stdout.strip()

        if output:
            first_line = output.splitlines()[0]
            return int(first_line)

    except Exception as e:
        print(f"[!] 获取 Git 首次提交时间失败: {file_path} - {e}")

    return None


# ============================================================
# 时间缓存
# ============================================================

def safe_load_time_cache(cache_file):
    """
    安全读取 .post_timestamps.json。
    """

    if not os.path.exists(cache_file):
        return {}

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        print("[!] 时间戳缓存格式不是字典，已忽略")
        return {}

    except Exception as e:
        print(f"[!] 时间戳缓存读取失败: {e}")
        return {}


# ============================================================
# 文件名 → 页面标题
# ============================================================

def get_display_title(file_name):
    """
    例如：

    HTB-Nomad-Notes-Writeup.md
        ↓
    HTB NOMAD NOTES WRITEUP
    """

    clean_name = file_name[:-3]

    return (
        clean_name
        .replace("-", " ")
        .replace("_", " ")
        .strip()
        .upper()
    )


# ============================================================
# 文件名 → URL
# ============================================================

def get_page_url(file_name):
    """
    保留你现在的网站 URL 结构：

    /p/HTB%20Nomad%20Notes%20Writeup
    """

    clean_name = file_name[:-3]

    encoded_name = urllib.parse.quote(
        clean_name,
        safe=""
    )

    return f"/{ROUTE_PREFIX}/{encoded_name}"


# ============================================================
# Markdown 清理
# ============================================================

def remove_front_matter(markdown_text):
    """
    如果以后 Markdown 使用：

    ---
    title: xxx
    description: xxx
    ---

    这里会把 front matter 去掉。

    当前没有 front matter 的文章也完全兼容。
    """

    if markdown_text.startswith("---"):
        match = re.match(
            r"^---\s*\n.*?\n---\s*\n",
            markdown_text,
            flags=re.DOTALL
        )

        if match:
            return markdown_text[match.end():]

    return markdown_text


def markdown_to_html(markdown_text):
    """
    Markdown → HTML

    开启：
    - fenced_code
    - tables
    - attr_list
    - sane_lists
    """

    markdown_text = remove_front_matter(markdown_text)

    return markdown.markdown(
        markdown_text,
        extensions=[
            "fenced_code",
            "tables",
            "attr_list",
            "sane_lists"
        ]
    )


# ============================================================
# 提取纯文本
# ============================================================

def html_to_plain_text(html_text):
    """
    用于生成 meta description。
    """

    text = re.sub(
        r"<script\b[^>]*>.*?</script>",
        " ",
        html_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(
        r"<style\b[^>]*>.*?</style>",
        " ",
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    text = re.sub(r"<[^>]+>", " ", text)

    text = html.unescape(text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def generate_description(markdown_text, title):
    """
    自动生成 SEO description。

    优先使用正文前 160~180 个字符。
    """

    clean_markdown = remove_front_matter(markdown_text)

    article_html = markdown_to_html(clean_markdown)

    plain_text = html_to_plain_text(article_html)

    if not plain_text:
        return f"{title} - SYC Cyber Security Writeups."

    # 去掉标题本身开头重复
    if plain_text.upper().startswith(title.upper()):
        plain_text = plain_text[len(title):].strip(" -:：")

    description = plain_text[:170].strip()

    if len(plain_text) > 170:
        description += "..."

    return description


# ============================================================
# 静态文章 HTML 模板
# ============================================================

def generate_article_html(
    file_name,
    title,
    description,
    canonical_url,
    article_content
):
    """
    生成完整静态 HTML。

    关键点：

    Google 首次请求页面时，
    title / description / h1 / 正文
    全部已经存在于 HTML 中。

    JS 只负责：
    - 主题
    - 动态背景
    - 阅读进度
    - highlight.js
    """

    safe_title = html.escape(title, quote=True)
    safe_description = html.escape(description, quote=True)
    safe_canonical = html.escape(canonical_url, quote=True)

    safe_file_name = html.escape(
        file_name.upper(),
        quote=True
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>{safe_title} | SYC</title>

<meta
    name="description"
    content="{safe_description}"
>

<meta
    name="robots"
    content="index, follow"
>

<link
    rel="canonical"
    href="{safe_canonical}"
>

<meta
    property="og:title"
    content="{safe_title} | SYC"
>

<meta
    property="og:description"
    content="{safe_description}"
>

<meta
    property="og:type"
    content="article"
>

<meta
    property="og:url"
    content="{safe_canonical}"
>

<meta
    property="og:site_name"
    content="SYC"
>

<meta
    name="twitter:card"
    content="summary"
>

<meta
    name="twitter:title"
    content="{safe_title} | SYC"
>

<meta
    name="twitter:description"
    content="{safe_description}"
>

<link rel="icon" type="image/png" href="/favicon.png">

<link
    rel="shortcut icon"
    href="/favicon.ico"
    type="image/x-icon"
>

<link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=Fira+Code&display=swap"
    rel="stylesheet"
>

<link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github-dark.min.css"
    id="hljs-style"
>

<script
    src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"
    defer
></script>


<style>

:root[data-theme="dark"] {{
    --bg-1: #050505;
    --bg-2: #0a0c1a;
    --bg-3: #120d1a;
    --text-main: #ffffff;
    --text-dim: rgba(255, 255, 255, 0.5);
    --accent: #ffffff;
    --canvas-opacity: 0.9;
    --code-bg: rgba(0, 0, 0, 0.5);
}}

:root[data-theme="light"] {{
    --bg-1: #fdfdfd;
    --bg-2: #f0f4ff;
    --bg-3: #f9f0ff;
    --text-main: #000000;
    --text-dim: rgba(0, 0, 0, 0.5);
    --accent: #000000;
    --canvas-opacity: 0.5;
    --code-bg: rgba(0, 0, 0, 0.05);
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    transition:
        background-color 0.6s,
        color 0.4s;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    background:
        linear-gradient(
            125deg,
            var(--bg-1),
            var(--bg-2),
            var(--bg-3),
            var(--bg-1)
        );

    background-size: 400% 400%;

    animation:
        spaceFlow 25s ease infinite;

    color: var(--text-main);

    font-family:
        'Inter',
        -apple-system,
        BlinkMacSystemFont,
        sans-serif;

    line-height: 1.8;

    overflow-x: hidden;
}}

@keyframes spaceFlow {{
    0% {{
        background-position: 0% 50%;
    }}

    50% {{
        background-position: 100% 50%;
    }}

    100% {{
        background-position: 0% 50%;
    }}
}}

#article-canvas {{
    position: fixed;
    top: 0;
    left: 0;

    width: 100%;
    height: 100%;

    z-index: -1;

    pointer-events: none;

    opacity: var(--canvas-opacity);
}}

.theme-toggle {{
    position: fixed;

    bottom: 30px;
    right: 30px;

    width: 48px;
    height: 48px;

    border-radius: 50%;

    background: var(--text-main);
    color: var(--bg-1);

    border: none;

    cursor: pointer;

    z-index: 2000;

    display: flex;
    align-items: center;
    justify-content: center;

    font-family: 'Fira Code';

    font-size: 10px;

    font-weight: bold;

    box-shadow:
        0 10px 30px rgba(0,0,0,0.2);
}}

#progress {{
    position: fixed;

    top: 0;
    left: 0;

    height: 3px;

    background: var(--accent);

    width: 0%;

    z-index: 2000;
}}

nav {{
    padding: 25px 40px;

    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);

    position: sticky;

    top: 0;

    z-index: 1000;

    display: flex;

    justify-content: space-between;

    align-items: center;
}}

nav a {{
    color: var(--text-dim);

    text-decoration: none;

    font-size: 11px;

    font-family: 'Fira Code';

    letter-spacing: 1px;
}}

nav a:hover {{
    color: var(--text-main);
}}

.content-wrapper {{
    max-width: 900px;

    margin: 40px auto;

    padding: 40px 24px;

    min-height: 80vh;
}}

.article-header {{
    margin-bottom: 70px;
}}

.article-header h1 {{
    font-size:
        clamp(32px, 7vw, 64px);

    font-weight: 700;

    color: var(--text-main);

    letter-spacing: -4px;

    line-height: 1;

    text-transform: uppercase;
}}

.article-meta {{
    margin-top: 20px;

    color: var(--text-dim);

    font-family: 'Fira Code';

    font-size: 11px;

    letter-spacing: 1px;
}}

.markdown-body {{
    overflow-wrap: break-word;
}}

.markdown-body img {{
    max-width: 100%;

    height: auto;

    border-radius: 12px;

    margin: 30px 0;

    display: block;

    box-shadow:
        0 20px 50px rgba(0,0,0,0.1);
}}

.markdown-body h1 {{
    font-size: 38px;

    margin: 50px 0 20px;

    color: var(--text-main);
}}

.markdown-body h2 {{
    font-size: 28px;

    margin: 50px 0 20px;

    color: var(--text-main);

    border-bottom:
        1px solid var(--text-dim);

    padding-bottom: 8px;
}}

.markdown-body h3 {{
    font-size: 22px;

    margin: 40px 0 15px;

    color: var(--text-main);
}}

.markdown-body p {{
    margin-bottom: 25px;

    font-size: 17px;

    opacity: 0.85;
}}

.markdown-body ul,
.markdown-body ol {{
    margin: 20px 0 25px;

    padding-left: 30px;
}}

.markdown-body li {{
    margin-bottom: 8px;
}}

.markdown-body a {{
    color: var(--text-main);

    text-decoration:
        underline;

    text-underline-offset: 4px;
}}

.markdown-body blockquote {{
    margin: 25px 0;

    padding: 15px 20px;

    border-left:
        3px solid var(--text-main);

    color: var(--text-dim);
}}

.markdown-body pre {{
    background:
        var(--code-bg) !important;

    padding: 25px;

    border:
        1px solid var(--text-dim);

    border-radius: 12px;

    margin: 30px 0;

    overflow-x: auto;

    backdrop-filter: blur(10px);
}}

.markdown-body code {{
    font-family: 'Fira Code';

    font-size: 14px;

    background:
        rgba(128,128,128,0.1);

    padding: 3px 6px;

    border-radius: 4px;
}}

.markdown-body pre code {{
    background: transparent;

    padding: 0;
}}

.markdown-body table {{
    width: 100%;

    border-collapse: collapse;

    margin: 30px 0;

    overflow-x: auto;
}}

.markdown-body th,
.markdown-body td {{
    border:
        1px solid var(--text-dim);

    padding: 10px;

    text-align: left;
}}

.markdown-body th {{
    color: var(--text-main);
}}

@media (max-width: 768px) {{

    .content-wrapper {{
        padding: 20px;
    }}

    nav {{
        padding: 15px 20px;
    }}

    .article-header h1 {{
        letter-spacing: -2px;
    }}

    .markdown-body p {{
        font-size: 16px;
    }}
}}

</style>

</head>


<body>

<div id="progress"></div>

<canvas id="article-canvas"></canvas>


<button
    class="theme-toggle"
    onclick="toggleTheme()"
>
    MODE
</button>


<nav>

<a href="/">
    &lt;- BACK_TO_TERMINAL
</a>

<span
    id="reading-id"
    style="
        font-family:'Fira Code';
        font-size:10px;
        color:var(--text-dim);
    "
>
    SYSTEM: SYNCED
</span>

</nav>


<main class="content-wrapper">

<header class="article-header">

<h1>
{safe_title}
</h1>

<div class="article-meta">
    {safe_file_name}
</div>

</header>


<article class="markdown-body">

{article_content}

</article>

</main>


<script>

/* ==========================================================
   Theme
   ========================================================== */

function toggleTheme() {{

    const root =
        document.documentElement;

    const target =
        root.getAttribute('data-theme') === 'dark'
            ? 'light'
            : 'dark';

    root.setAttribute(
        'data-theme',
        target
    );

    localStorage.setItem(
        'theme',
        target
    );

    const style =
        document.getElementById(
            'hljs-style'
        );

    if (style) {{

        style.href =
            target === 'dark'
                ? "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github-dark.min.css"
                : "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css";
    }}
}}


/* ==========================================================
   Restore Theme
   ========================================================== */

try {{

    document.documentElement
        .setAttribute(
            'data-theme',
            localStorage.getItem('theme') || 'dark'
        );

}} catch (e) {{

    document.documentElement
        .setAttribute(
            'data-theme',
            'dark'
        );
}}


/* ==========================================================
   Code Highlight
   ========================================================== */

window.addEventListener(
    'load',
    () => {{

        if (
            window.hljs
        ) {{

            document
                .querySelectorAll(
                    'pre code'
                )
                .forEach(
                    (el) => {{
                        hljs.highlightElement(el);
                    }}
                );
        }}

    }}
);


/* ==========================================================
   Reading ID
   ========================================================== */

document
    .getElementById('reading-id')
    .innerText =
        'SYSTEM: {safe_file_name}';


/* ==========================================================
   Reading Progress
   ========================================================== */

window.addEventListener(
    'scroll',
    () => {{

        const winScroll =
            document.documentElement.scrollTop;

        const height =
            document.documentElement.scrollHeight -
            document.documentElement.clientHeight;

        const percentage =
            height > 0
                ? (winScroll / height) * 100
                : 0;

        document
            .getElementById('progress')
            .style.width =
                percentage + '%';

    }}
);


/* ==========================================================
   Dynamic Background
   ========================================================== */

const canvas =
    document.getElementById(
        'article-canvas'
    );

const ctx =
    canvas.getContext('2d');

let fluidNodes = [];

let trailParticles = [];

const mouse = {{
    x: -500,
    y: -500
}};


function initCanvas() {{

    canvas.width =
        window.innerWidth;

    canvas.height =
        window.innerHeight;

    fluidNodes =
        Array.from(
            {{ length: 3 }},
            () => ({{

                x:
                    Math.random() *
                    canvas.width,

                y:
                    Math.random() *
                    canvas.height,

                vx:
                    (Math.random() - 0.5) *
                    0.4,

                vy:
                    (Math.random() - 0.5) *
                    0.4,

                size:
                    Math.random() *
                    (canvas.width * 0.4) +
                    canvas.width * 0.3
            }})
        );
}}


window.onmousemove =
    (e) => {{

        mouse.x =
            e.clientX;

        mouse.y =
            e.clientY;

        for (
            let i = 0;
            i < 2;
            i++
        ) {{

            trailParticles.push(
                new Particle(
                    mouse.x,
                    mouse.y
                )
            );
        }}
    }};


class Particle {{

    constructor(x, y) {{

        this.x = x;

        this.y = y;

        this.vx =
            (Math.random() - 0.5) *
            1.5;

        this.vy =
            (Math.random() - 0.5) *
            1.5;

        this.life = 1.0;

        this.decay =
            0.015 +
            Math.random() * 0.02;

        this.size =
            Math.random() * 2.5 +
            0.5;
    }}

    update() {{

        this.x += this.vx;

        this.y += this.vy;

        this.life -= this.decay;
    }}

    draw(color) {{

        ctx.fillStyle =
            `rgba(${{color}}, ${{this.life * 0.4}})`;

        ctx.beginPath();

        ctx.arc(
            this.x,
            this.y,
            this.size,
            0,
            Math.PI * 2
        );

        ctx.fill();
    }}
}}


function draw() {{

    const isDark =
        document.documentElement
            .getAttribute(
                'data-theme'
            ) === 'dark';

    ctx.fillStyle =
        isDark
            ? "rgba(5, 5, 5, 0.15)"
            : "rgba(253, 253, 253, 0.15)";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    ctx.globalCompositeOperation =
        isDark
            ? "lighter"
            : "multiply";


    const colorRGB =
        isDark
            ? "60, 70, 100"
            : "200, 210, 240";


    fluidNodes.forEach(
        node => {{

            node.x += node.vx;

            node.y += node.vy;


            if (
                node.x < 0 ||
                node.x > canvas.width
            ) {{
                node.vx *= -1;
            }}


            if (
                node.y < 0 ||
                node.y > canvas.height
            ) {{
                node.vy *= -1;
            }}


            const g =
                ctx.createRadialGradient(
                    node.x,
                    node.y,
                    0,
                    node.x,
                    node.y,
                    node.size
                );


            g.addColorStop(
                0,
                `rgba(${{colorRGB}}, 0.3)`
            );

            g.addColorStop(
                1,
                "transparent"
            );


            ctx.fillStyle = g;

            ctx.beginPath();

            ctx.arc(
                node.x,
                node.y,
                node.size,
                0,
                Math.PI * 2
            );

            ctx.fill();

        }}
    );


    ctx.globalCompositeOperation =
        "source-over";


    const particleRGB =
        isDark
            ? "255, 255, 255"
            : "0, 0, 0";


    trailParticles.forEach(
        (p, i) => {{

            p.update();

            p.draw(
                particleRGB
            );

            if (
                p.life <= 0
            ) {{
                trailParticles.splice(
                    i,
                    1
                );
            }}
        }}
    );


    requestAnimationFrame(
        draw
    );
}}


window.addEventListener(
    'resize',
    initCanvas
);

initCanvas();

draw();

</script>

</body>

</html>
"""


# ============================================================
# 生成全部文章页面
# ============================================================

def generate_article_pages(files_with_time):
    """
    为 posts/ 下每一篇 Markdown
    生成一个：

    articles/<文件名>/index.html

    例如：

    posts/
        HTB-Nomad-Notes-Writeup.md

    ↓

    articles/
        HTB-Nomad-Notes-Writeup/
            index.html
    """

    os.makedirs(
        ARTICLES_DIR,
        exist_ok=True
    )

    generated_files = set()

    for file_name, timestamp in files_with_time:

        file_path = os.path.join(
            POSTS_DIR,
            file_name
        )

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                markdown_text = f.read()

        except Exception as e:

            print(
                f"[!] 无法读取文章: "
                f"{file_path} - {e}"
            )

            continue


        title =
            get_display_title(
                file_name
            )

        description =
            generate_description(
                markdown_text,
                title
            )

        page_url =
            get_page_url(
                file_name
            )

        canonical_url =
            f"{BASE_URL}{page_url}"


        article_content =
            markdown_to_html(
                markdown_text
            )


        # 为每篇文章创建独立目录
        clean_name =
            file_name[:-3]

        article_dir =
            os.path.join(
                ARTICLES_DIR,
                clean_name
            )

        os.makedirs(
            article_dir,
            exist_ok=True
        )


        output_file =
            os.path.join(
                article_dir,
                "index.html"
            )


        full_html =
            generate_article_html(
                file_name=file_name,
                title=title,
                description=description,
                canonical_url=canonical_url,
                article_content=article_content
            )


        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(full_html)


        generated_files.add(
            os.path.normpath(
                output_file
            )
        )


        print(
            f"[+] 生成文章 HTML: "
            f"{output_file}"
        )


    # 清理已经删除的文章 HTML
    if os.path.exists(ARTICLES_DIR):

        for root, dirs, files in os.walk(
            ARTICLES_DIR,
            topdown=False
        ):

            for file_name in files:

                path =
                    os.path.normpath(
                        os.path.join(
                            root,
                            file_name
                        )
                    )

                if path not in generated_files:

                    try:

                        os.remove(path)

                        print(
                            f"[-] 删除旧文章 HTML: "
                            f"{path}"
                        )

                    except Exception as e:

                        print(
                            f"[!] 删除失败: "
                            f"{path} - {e}"
                        )


            # 删除空目录
            for directory in dirs:

                directory_path =
                    os.path.join(
                        root,
                        directory
                    )

                try:

                    if not os.listdir(
                        directory_path
                    ):

                        os.rmdir(
                            directory_path
                        )

                except Exception:
                    pass


# ============================================================
# 主生成逻辑
# ============================================================

def generate_site_assets():

    if not os.path.exists(
        POSTS_DIR
    ):

        os.makedirs(
            POSTS_DIR
        )

        print(
            f"[*] 已创建目录: "
            f"{POSTS_DIR}"
        )


    time_cache =
        safe_load_time_cache(
            TIME_CACHE_FILE
        )


    if time_cache:

        print(
            "[*] 已加载时间戳缓存"
        )

    else:

        print(
            "[*] 没有可用时间戳缓存，"
            "将尝试从 Git 历史生成"
        )


    files_with_time = []

    current_files = set()


    # ========================================================
    # 扫描 Markdown
    # ========================================================

    for file_name in os.listdir(
        POSTS_DIR
    ):

        if not file_name.endswith(
            ".md"
        ):

            continue


        current_files.add(
            file_name
        )


        file_path =
            os.path.join(
                POSTS_DIR,
                file_name
            )


        # 1. 优先使用缓存
        if file_name in time_cache:

            try:

                timestamp =
                    int(
                        time_cache[
                            file_name
                        ]
                    )

                print(
                    f"[*] 使用缓存时间: "
                    f"{file_name} -> "
                    f"{timestamp}"
                )

            except Exception:

                print(
                    f"[!] 缓存时间异常，"
                    f"重新获取: {file_name}"
                )

                timestamp = None

        else:

            timestamp = None


        # 2. 从 Git 获取
        if timestamp is None:

            git_timestamp =
                get_first_git_timestamp(
                    file_path
                )


            if git_timestamp:

                timestamp =
                    git_timestamp

                print(
                    f"[+] 使用 Git 首次提交时间: "
                    f"{file_name} -> "
                    f"{timestamp}"
                )

            else:

                # 3. 最终兜底
                timestamp =
                    int(
                        datetime.now(
                            TZ
                        ).timestamp()
                    )

                print(
                    f"[+] 使用当前运行时间兜底: "
                    f"{file_name} -> "
                    f"{timestamp}"
                )


            time_cache[
                file_name
            ] = timestamp


        files_with_time.append(
            (
                file_name,
                timestamp
            )
        )


    # ========================================================
    # 清理时间缓存
    # ========================================================

    cleaned_time_cache = {

        name: int(ts)

        for name, ts
        in time_cache.items()

        if name in current_files
    }


    time_cache =
        cleaned_time_cache


    # ========================================================
    # 按首次上传时间倒序
    # ========================================================

    files_with_time.sort(
        key=lambda x: x[1],
        reverse=True
    )


    # ========================================================
    # 生成文章 HTML
    # ========================================================

    print(
        "\n[*] 开始生成静态文章 HTML..."
    )

    generate_article_pages(
        files_with_time
    )


    # ========================================================
    # list.json
    # ========================================================

    posts_data = []


    sitemap_content = [

        '<?xml version="1.0" encoding="UTF-8"?>',

        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',

        '  <url>',

        f'    <loc>{BASE_URL}/</loc>',

        '    <priority>1.0</priority>',

        '  </url>'
    ]


    for file_name, timestamp in files_with_time:

        dt =
            datetime.fromtimestamp(
                timestamp,
                TZ
            )


        date_str =
            dt.strftime(
                "%Y-%m-%d"
            )


        time_str =
            dt.strftime(
                "%H:%M:%S"
            )


        clean_name =
            file_name[:-3]


        display_title =
            get_display_title(
                file_name
            )


        page_url =
            get_page_url(
                file_name
            )


        static_url =
            f"{BASE_URL}{page_url}"


        posts_data.append({

            "fileName":
                file_name,

            "title":
                display_title,

            "url":
                page_url,

            "date":
                date_str,

            "time":
                time_str,

            "timestamp":
                timestamp
        })


        sitemap_content.append(
            "  <url>"
        )

        sitemap_content.append(
            f"    <loc>{html.escape(static_url)}</loc>"
        )

        sitemap_content.append(
            f"    <lastmod>{date_str}</lastmod>"
        )

        sitemap_content.append(
            "    <priority>0.8</priority>"
        )

        sitemap_content.append(
            "  </url>"
        )


    # ========================================================
    # 写入 list.json
    # ========================================================

    with open(
        LIST_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            posts_data,
            f,
            indent=4,
            ensure_ascii=False
        )


    print(
        f"[+] 成功更新前端索引: "
        f"{len(posts_data)} 篇文章"
    )


    # ========================================================
    # 写入 sitemap.xml
    # ========================================================

    sitemap_content.append(
        "</urlset>"
    )


    with open(
        SITEMAP_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(
                sitemap_content
            )
        )


    print(
        f"[+] 成功更新站点地图: "
        f"{SITEMAP_FILE}"
    )


    # ========================================================
    # 写入 robots.txt
    # ========================================================

    with open(
        ROBOTS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "User-agent: *\n"
        )

        f.write(
            "Allow: /\n"
        )

        f.write(
            f"Sitemap: "
            f"{BASE_URL}/{SITEMAP_FILE}\n"
        )


    print(
        "[+] 成功生成 robots.txt"
    )


    # ========================================================
    # 保存时间缓存
    # ========================================================

    with open(
        TIME_CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            time_cache,
            f,
            indent=4,
            ensure_ascii=False
        )


    print(
        "[+] 已保存时间戳缓存到 "
        f"{TIME_CACHE_FILE}"
    )


    print(
        "[+] 文章已按首次上传时间降序排列"
    )

    print(
        "[+] SEO 静态文章 HTML 生成完成"
    )


# ============================================================
# Entry
# ============================================================

if __name__ == "__main__":

    generate_site_assets()
```
