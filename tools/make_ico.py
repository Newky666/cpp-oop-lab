#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_ico.py - 生成 OOP Lab 图标（纯标准库, 完全可复现）

设计寓意: 深蓝→紫渐变圆角底 + 「类继承关系图」——
上面一个父类方块, 下面是两个子类方块, 中间用连线相连。
一眼看出是「面向对象」, 且 16×16 下三个方块仍能辨认。

产物（相对项目根）:
    oop_lab.ico                 多尺寸 PNG-in-ICO, 交给 PyInstaller --icon
    oop_lab_icon.py             64×64 PNG 的 base64 常量模块(窗口 iconphoto 用)
    docs/icon/oop_lab_256.png   大图存档, 方便以后改配色

用法:
    py tools/make_ico.py
"""

from __future__ import annotations

import base64
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---- 配色（想换风格改这里） ----
BG_TOP = (0x18, 0x2A, 0x6B)          # 渐变起点: 深蓝
BG_BOTTOM = (0x7A, 0x2F, 0xA8)       # 渐变终点: 紫
PARENT_FILL = (0x8F, 0xDC, 0xFF)     # 父类方块: 亮青
CHILD_FILL = (0xF4, 0xF8, 0xFF)      # 子类方块: 近白
EDGE_FILL = (0xBF, 0xE9, 0xFF)       # 连线

SS = 2                               # 超采样倍率(抗锯齿)
ICO_SIZES = (256, 128, 64, 48, 32, 16)


class Canvas:
    """RGBA 画布 + 圆角矩形/线段/渐变填充（都是纯 Python, 一次性生成够用）。"""

    def __init__(self, size: int) -> None:
        self.size = size
        self.buf = bytearray(size * size * 4)

    def _put(self, x: int, y: int, color, alpha: int = 255) -> None:
        if not (0 <= x < self.size and 0 <= y < self.size) or alpha <= 0:
            return
        index = (y * self.size + x) * 4
        if alpha >= 255:
            self.buf[index:index + 4] = bytes((color[0], color[1], color[2], 255))
        else:
            keep = 255 - alpha
            self.buf[index] = (self.buf[index] * keep + color[0] * alpha) // 255
            self.buf[index + 1] = (self.buf[index + 1] * keep + color[1] * alpha) // 255
            self.buf[index + 2] = (self.buf[index + 2] * keep + color[2] * alpha) // 255
            self.buf[index + 3] = min(255, self.buf[index + 3] + alpha)

    # ---- 形状 -------------------------------------------------------
    @staticmethod
    def _in_round_rect(px: float, py: float, x0, y0, x1, y1, radius) -> bool:
        if px < x0 or px > x1 or py < y0 or py > y1:
            return False
        cx = min(max(px, x0 + radius), x1 - radius)
        cy = min(max(py, y0 + radius), y1 - radius)
        dx, dy = px - cx, py - cy
        return dx * dx + dy * dy <= radius * radius

    def round_rect(self, x0, y0, x1, y1, radius, color, gradient=None) -> None:
        """填充圆角矩形; gradient=(color0, color1) 时沿对角线渐变。"""
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                if not self._in_round_rect(x + 0.5, y + 0.5, x0, y0, x1, y1, radius):
                    continue
                if gradient is None:
                    self._put(x, y, color)
                else:
                    # 归一化对角位置 (0..1) 作为渐变参数
                    t = ((x - x0) + (y - y0)) / max(1.0, (x1 - x0) + (y1 - y0))
                    mix = tuple(int(gradient[0][i] + (gradient[1][i] - gradient[0][i]) * t)
                                for i in range(3))
                    self._put(x, y, mix)

    def line(self, x0, y0, x1, y1, width, color) -> None:
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        half = width / 2.0
        for step in range(steps + 1):
            t = step / steps if steps else 0.0
            cx = x0 + (x1 - x0) * t
            cy = y0 + (y1 - y0) * t
            for y in range(int(cy - half), int(cy + half) + 1):
                for x in range(int(cx - half), int(cx + half) + 1):
                    if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= half * half + 0.25:
                        self._put(x, y, color)


def downsample(src: bytearray, src_size: int, dst_size: int) -> bytearray:
    """盒式降采样（整数倍）—— 超采样抗锯齿的最后一步。"""
    factor = src_size // dst_size
    out = bytearray(dst_size * dst_size * 4)
    area = factor * factor
    for y in range(dst_size):
        for x in range(dst_size):
            r = g = b = a = 0
            for dy in range(factor):
                row = ((y * factor + dy) * src_size + x * factor) * 4
                for dx in range(factor):
                    idx = row + dx * 4
                    alpha = src[idx + 3]
                    r += src[idx] * alpha
                    g += src[idx + 1] * alpha
                    b += src[idx + 2] * alpha
                    a += alpha
            out_idx = (y * dst_size + x) * 4
            if a:
                out[out_idx] = r // a
                out[out_idx + 1] = g // a
                out[out_idx + 2] = b // a
            out[out_idx + 3] = a // area
    return out


def render(size: int, ss: int = SS) -> bytearray:
    """渲染一张 size×size 的 RGBA 图。坐标全部用归一化值描述。"""
    big = size * ss
    canvas = Canvas(big)
    unit = float(big)

    def px(v: float) -> float:
        return v * unit

    # 1) 渐变圆角底
    canvas.round_rect(px(0.04), px(0.04), px(0.96), px(0.96),
                      px(0.20), None, gradient=(BG_TOP, BG_BOTTOM))
    # 2) 父类方块
    canvas.round_rect(px(0.24), px(0.17), px(0.76), px(0.35), px(0.045), PARENT_FILL)
    # 3) 继承连线: 父类底部 -> 中点 -> 两个子类顶部
    width_line = px(0.022)
    canvas.line(px(0.50), px(0.35), px(0.50), px(0.47), width_line, EDGE_FILL)
    canvas.line(px(0.30), px(0.47), px(0.70), px(0.47), width_line, EDGE_FILL)
    canvas.line(px(0.30), px(0.47), px(0.30), px(0.60), width_line, EDGE_FILL)
    canvas.line(px(0.70), px(0.47), px(0.70), px(0.60), width_line, EDGE_FILL)
    # 4) 两个子类方块
    canvas.round_rect(px(0.15), px(0.60), px(0.45), px(0.78), px(0.04), CHILD_FILL)
    canvas.round_rect(px(0.55), px(0.60), px(0.85), px(0.78), px(0.04), CHILD_FILL)

    return downsample(canvas.buf, big, size) if ss > 1 else canvas.buf


def encode_png(width: int, height: int, rgba: bytearray) -> bytes:
    """RGBA -> PNG（stdlib: struct + zlib）；每行前加一个 filter=0 字节。"""
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw.extend(rgba[y * stride:(y + 1) * stride])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def encode_ico(images) -> bytes:
    """PNG-in-ICO: ICONDIR + ICONDIRENTRY×N + 各尺寸 PNG（Vista+ 全支持）。"""
    images = sorted(images, key=lambda item: -item[0])
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = bytearray()
    blobs = bytearray()
    for size, png in images:
        edge = 0 if size >= 256 else size        # 256 在 ICO 里写 0
        entries.extend(struct.pack("<BBBBHHII", edge, edge, 0, 0, 1, 32,
                                   len(png), offset))
        offset += len(png)
        blobs.extend(png)
    return bytes(header + entries + blobs)


def main() -> int:
    # 大图渲染一次, 逐级降采样得到 256/128/64/32/16
    base = render(256, ss=SS)
    images = []
    for size in ICO_SIZES:
        if size == 48:                       # 不能整除 256, 单独渲染
            rgba = render(48, ss=4)
        elif size == 256:
            rgba = base
        else:
            rgba = downsample(base, 256, size)
        images.append((size, encode_png(size, size, rgba)))

    ico_path = os.path.join(ROOT, "oop_lab.ico")
    with open(ico_path, "wb") as fh:
        fh.write(encode_ico(images))

    # 64×64 的 base64 常量模块（窗口图标用, 免外部文件）
    png64 = dict((size, data) for size, data in images)[64]
    b64 = base64.b64encode(png64).decode("ascii")
    module = (
        '#!/usr/bin/env python3\n'
        '# -*- coding: utf-8 -*-\n'
        '"""oop_lab_icon.py - 图标数据（由 tools/make_ico.py 生成, 请勿手改）\n\n'
        '64×64 PNG 的 base64; 窗口启动时 iconphoto 用, 不依赖外部文件。\n'
        '"""\n\n'
        'ICON_PNG_B64 = (\n'
    )
    for index in range(0, len(b64), 96):
        module += '    "%s"\n' % b64[index:index + 96]
    module += ')\n'
    with open(os.path.join(ROOT, "oop_lab_icon.py"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(module)

    # 大图存档
    icon_dir = os.path.join(ROOT, "docs", "icon")
    os.makedirs(icon_dir, exist_ok=True)
    with open(os.path.join(icon_dir, "oop_lab_256.png"), "wb") as fh:
        fh.write(dict(images)[256])

    print("已生成:")
    print("  %s  (%.1f KB, %d 个尺寸)" % (ico_path, os.path.getsize(ico_path) / 1024.0,
                                          len(images)))
    print("  %s" % os.path.join(ROOT, "oop_lab_icon.py"))
    print("  %s" % os.path.join(icon_dir, "oop_lab_256.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
