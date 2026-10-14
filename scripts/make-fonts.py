# -*- coding: utf-8 -*-
"""허브 글꼴(Pretendard) 줄인 파일 만들기.

만든 파일은 assets/fonts/ 에 커밋해 둠. 글꼴 버전을 바꾸거나 남길 글자를 바꿀 때만 다시 돌림.
- 원본: Pretendard 1.3.9 woff2 (cslog `apps/webapp/web-vue/src/assets/fonts` 와 같은 파일).
- 남기는 글자: KS X 1001 한글 2,350자 + 이 저장소 문서·기록 글에 실제로 쓰인 글자 + 한글 자모·영문·숫자·기호.
  목록 밖 글자는 다음 글꼴(맑은 고딕)로 그려짐.
- 원본 1벌 약 760KB → 약 200KB.

사용: python scripts/make-fonts.py <원본 woff2 폴더>
의존성: fonttools, brotli
"""
import os
import sys

from fontTools import subset

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "fonts")
WEIGHTS = ["Regular", "Medium", "Bold"]

# 영문·숫자·문장부호·화살표·도형·원문자·표 선·전각 기호 등
RANGES = [
    (0x0020, 0x007E), (0x00A0, 0x017F), (0x2000, 0x206F), (0x2070, 0x209F), (0x20A0, 0x20CF),
    (0x2100, 0x218F), (0x2190, 0x21FF), (0x2200, 0x22FF), (0x2300, 0x23FF), (0x2460, 0x24FF),
    (0x2500, 0x257F), (0x25A0, 0x25FF), (0x2600, 0x26FF), (0x2700, 0x27BF), (0x3000, 0x303F),
    (0x3131, 0x318E), (0x3200, 0x32FF), (0x3300, 0x33FF), (0xFF01, 0xFF60),
]


def ksx1001_hangul():
    """KS X 1001 완성형 한글 2,350자 (EUC-KR 0xB0A1~0xC8FE)."""
    out = set()
    for hi in range(0xB0, 0xC9):
        for lo in range(0xA1, 0xFF):
            try:
                ch = bytes([hi, lo]).decode("euc-kr")
            except UnicodeDecodeError:
                continue
            if "가" <= ch <= "힣":
                out.add(ch)
    return out


def used_chars():
    """문서·기록 글·빌드 스크립트·디자인 문서에 실제로 쓰인 글자."""
    out = set()
    targets = [os.path.join(ROOT, "docs"), os.path.join(ROOT, "posts")]
    files = [os.path.join(ROOT, "scripts", "build.py"), os.path.join(ROOT, "design-system.md")]
    for d in targets:
        if os.path.isdir(d):
            files += [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md")]
    for path in files:
        with open(path, encoding="utf-8") as f:
            out.update(f.read())
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit("사용: python scripts/make-fonts.py <원본 woff2 폴더>")
    src_dir = sys.argv[1]
    codepoints = {c for a, b in RANGES for c in range(a, b + 1)}
    codepoints |= {ord(c) for c in ksx1001_hangul()}
    codepoints |= {ord(c) for c in used_chars() if ord(c) >= 0x20}
    os.makedirs(OUT, exist_ok=True)
    for w in WEIGHTS:
        src = os.path.join(src_dir, "Pretendard-%s.woff2" % w)
        dst = os.path.join(OUT, "Pretendard-%s.subset.woff2" % w)
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["*"]
        opts.name_IDs = ["*"]
        opts.name_languages = ["*"]
        font = subset.load_font(src, opts)
        sub = subset.Subsetter(opts)
        sub.populate(unicodes=codepoints)
        sub.subset(font)
        subset.save_font(font, dst, opts)
        kept = font.getBestCmap()
        hangul = sum(1 for c in kept if 0xAC00 <= c <= 0xD7A3)
        print("%s  %d KB  (글자 %d, 한글 %d)" % (os.path.relpath(dst, ROOT), os.path.getsize(dst) // 1024, len(kept), hangul))


if __name__ == "__main__":
    main()
