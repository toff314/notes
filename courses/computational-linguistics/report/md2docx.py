# -*- coding: utf-8 -*-
"""极简作业转换：Markdown -> docx。正文五号宋体单倍行距，仅标题分级放大。"""
import sys, re
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def set_font(run, size, bold=False, name_cn='宋体', name_en='Times New Roman'):
    run.font.size = Pt(size); run.font.bold = bold
    run.font.name = name_en
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name_cn)

def convert(md_path, docx_path):
    doc = Document()
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)   # A4
        s.top_margin = s.bottom_margin = Cm(2.54)
        s.left_margin = s.right_margin = Cm(3.17)
    lines = open(md_path, encoding='utf-8').read().split('\n')
    in_quote = in_code = False
    for ln in lines:
        s = ln.rstrip()
        if s.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            p = doc.add_paragraph(); r = p.add_run(s); set_font(r, 9, name_cn='宋体'); continue
        m = re.match(r'^(#{1,4})\s+(.*)', s)
        if m:
            level, text = len(m.group(1)), m.group(2).strip()
            size = {1: 16, 2: 14, 3: 12}.get(level, 12)
            p = doc.add_paragraph()
            if level == 1: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6 if level > 1 else 0)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run(text); set_font(r, size, bold=True, name_cn='黑体')
            continue
        if s.startswith('>'):
            s = s.lstrip('> ').strip()
            if not s: continue
            p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.74)
            r = p.add_run(s); set_font(r, 10.5)
            continue
        if re.match(r'^[-*]\s+', s):
            s = '• ' + re.sub(r'^[-*]\s+', '', s)
        if re.match(r'^\d+\.\s+', s) is None and re.match(r'^\|', s):
            continue  # 表格行转纯文本由下方处理
        # 粗体行内最小化：去 **，保留文字
        s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
        if not s.strip():
            continue
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.first_line_indent = Pt(21)   # 首行缩进两字符
        r = p.add_run(s); set_font(r, 10.5)
    doc.save(docx_path)
    print('saved:', docx_path)

if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
