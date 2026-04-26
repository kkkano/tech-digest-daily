"""技术日报输出渲染器。"""

from renderers.json_renderer import render_json
from renderers.markdown import render_markdown

__all__ = ["render_json", "render_markdown"]
