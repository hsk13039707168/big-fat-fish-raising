#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《大肥鱼养成计划》单文件打包脚本
================================================================================
把 assets/ 下的全部素材以 base64（data URI）内嵌进 HTML，产出一个**零外部依赖**的
单文件网页：拷到任何电脑 / 手机，双击即可离线游玩。

用法
----
    python tools/bundle.py                       # 输出到 dist/
    python tools/bundle.py -o 我的游戏.html       # 指定输出文件

做了三件事
----------
1. 把页面里所有静态 `src="assets/xxx"` 直接替换成 data URI；
2. 在 <head> 注入 `window.EMBEDDED = {文件名: dataURI}` 映射表；
3. 给 `AssetLoader.candidates()` 打补丁：运行时换图（进化 / 表情 / 道具）
   优先查内嵌表，命中就直接返回 data URI，不再访问磁盘。

注意
----
* 统一使用 base64，不用原始 SVG 文本 —— SVG 里的换行符会破坏 <script> 字符串字面量。
* 产物约 12 MB，仅用于分发；开发请直接用源码版 `大肥鱼养成计划.html` + `assets/`。
"""
import argparse
import base64
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, '大肥鱼养成计划.html')
ASSETS = os.path.join(ROOT, 'assets')
DEFAULT_OUT = os.path.join(ROOT, 'dist', '大肥鱼养成计划_单文件版.html')

MIME = {
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
}


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = MIME.get(ext, 'application/octet-stream')
    with open(path, 'rb') as f:
        raw = f.read()
    return 'data:%s;base64,%s' % (mime, base64.b64encode(raw).decode('ascii'))


def main():
    ap = argparse.ArgumentParser(description='把游戏打包成内嵌素材的单文件 HTML')
    ap.add_argument('-s', '--src', default=SRC, help='源 HTML（默认 大肥鱼养成计划.html）')
    ap.add_argument('-o', '--out', default=DEFAULT_OUT, help='输出文件')
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding='utf-8')
    if not os.path.exists(args.src):
        sys.exit('找不到源 HTML: %s' % args.src)

    # 1) 收集素材
    files = sorted(f for f in os.listdir(ASSETS)
                  if os.path.splitext(f)[1].lower() in MIME)
    emb = {f: data_uri(os.path.join(ASSETS, f)) for f in files}
    print('内嵌素材 %d 个: %s' % (len(emb), ', '.join(files)))

    html = io.open(args.src, encoding='utf-8').read()

    # 2) 替换静态 src="assets/xxx"
    miss = []
    def repl(m):
        f = m.group(1)
        if f in emb:
            return 'src="%s"' % emb[f]
        miss.append(f)
        return m.group(0)
    html, n_static = re.subn(r'src="assets/([^"]+)"', repl, html)
    print('替换静态 src: %d 处；未找到素材: %s' % (n_static, miss))

    # 3) 注入内嵌映射表（放在 <head> 之后，确保早于任何游戏脚本执行）
    table = ',\n'.join('"%s":"%s"' % (k, v) for k, v in emb.items())
    inject = '<script>window.EMBEDDED={%s};</script>' % table
    if '<head>' not in html:
        sys.exit('源 HTML 缺少 <head>')
    html = html.replace('<head>', '<head>' + inject, 1)
    print('已注入 EMBEDDED 映射表（%d 项）' % len(emb))

    # 4) 给 AssetLoader.candidates() 打补丁：内嵌优先
    anchor = """  candidates(file){
    if(!file) return [];
    if(this.isAbs(file)) return [file];"""
    patch = """  candidates(file){
    if(!file) return [];
    if(this.isAbs(file)) return [file];
    if(window.EMBEDDED && window.EMBEDDED[file]) return [window.EMBEDDED[file]];   // 单文件版：内嵌优先"""
    if anchor not in html:
        sys.exit('!! 未找到 AssetLoader.candidates() 锚点，补丁未注入')
    html = html.replace(anchor, patch, 1)
    print('已注入 AssetLoader 内嵌优先分支')

    # 5) 自检：注入的脚本必须能被 JS 解析（换行 / </script 都会破坏语法）
    i = html.find('window.EMBEDDED=')
    s0 = html.rfind('<script>', 0, i) + len('<script>')
    s1 = html.find('</script>', i)
    io.open(os.path.join(HERE, '.bundle_check.js'), 'w', encoding='utf-8').write(html[s0:s1])
    print('已导出注入脚本供语法校验: tools/.bundle_check.js (%d 字节)' % (s1 - s0))

    # 6) 输出
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with io.open(args.out, 'w', encoding='utf-8') as f:
        f.write(html)

    left = re.findall(r'src="assets/', html)
    print('输出: %s' % os.path.relpath(args.out, ROOT))
    print('体积: %.1f MB' % (os.path.getsize(args.out) / 1048576.0))
    print('剩余外部资源引用: %d 处 %s' % (len(left), left[:5]))


if __name__ == '__main__':
    main()
