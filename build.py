#!/usr/bin/env python3
"""
Сборка сайта Merlot Wine&Dine.

Тексты лежат в content.json, витрина кухни — в menu.json, разметка —
в template.html. Чтобы что-то поменять: правите JSON и запускаете

    python3 build.py

Скрипт заново создаёт index.html (азербайджанский), ru/index.html,
en/index.html, а также sitemap.xml и robots.txt.
Готовые index.html руками не редактируйте: их перезапишет следующая сборка.

Своего онлайн-меню у ресторана нет, поэтому на сайте — четыре блюда с
фотографиями и кнопка в инстаграм, где ресторан выкладывает сеты и новинки.
Цены в menu.json необязательные: нет поля price — строка с ценой не рисуется.
"""

import html
import json
import os
import re
from datetime import date

# Адрес сайта. После подключения своего домена поменять на https://merlot.az
SITE = "https://alimressi.github.io/merlot"

LANGS = {
    "az": {"dir": "",    "label": "AZ", "locale": "az_AZ"},
    "ru": {"dir": "ru/", "label": "RU", "locale": "ru_RU"},
    "en": {"dir": "en/", "label": "EN", "locale": "en_US"},
}
DEFAULT = "az"


def url_for(lang):
    return SITE + "/" + LANGS[lang]["dir"]


def hreflang_block():
    rows = [
        f'<link rel="alternate" hreflang="{lg}" href="{url_for(lg)}">'
        for lg in LANGS
    ]
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{url_for(DEFAULT)}">')
    return "\n".join(rows)


def switcher(current):
    """Переключатель языков: настоящие ссылки, чтобы их видел поисковик."""
    out = []
    for lg, meta in LANGS.items():
        # с любой страницы поднимаемся в корень, оттуда в нужный язык
        up = "" if LANGS[current]["dir"] == "" else "../"
        href = (up + meta["dir"]) or "./"
        cur = ' aria-current="page"' if lg == current else ""
        out.append(
            f'        <a class="langs__btn" href="{href}" hreflang="{lg}"{cur}>{meta["label"]}</a>'
        )
    return "\n".join(out)


def price_text(value, lang):
    """1.5 -> «1,5 ₼», 14 -> «14 ₼». В английском дробная часть через точку."""
    if float(value) == int(value):
        num = str(int(value))
    else:
        num = f"{float(value):g}"
        if lang != "en":
            num = num.replace(".", ",")
    return f"{num} ₼"


def peek_block(menu, lang, asset_prefix):
    """Витрина кухни: блюда с фотографией, названием, составом и — если цена
    указана в menu.json — ценой."""
    e = html.escape
    cards = []
    for n, item in enumerate(menu["items"], 1):
        t = item[lang]
        desc = f'\n            <p class="dish__desc">{e(t["d"])}</p>' if t.get("d") else ""
        price = ""
        if item.get("price") is not None:
            price = f'\n          <p class="dish__price">{price_text(item["price"], lang)}</p>'
        cards.append(
            f"""        <article class="dish reveal">
          <figure class="dish__shot shot" data-ph="images/{item['img']}.webp">
            <img src="{asset_prefix}images/{item['img']}.webp" alt="{e(t['n'])}"
                 loading="lazy" decoding="async" width="512" height="640">
            <span class="dish__no">{n:02d}</span>
          </figure>
          <div class="dish__body">
            <h3 class="dish__name">{e(t['n'])}</h3>{desc}
          </div>{price}
        </article>"""
        )
    return '      <div class="dishes">\n' + "\n".join(cards) + "\n      </div>"


def build():
    tpl = open("template.html", encoding="utf-8").read()
    content = json.load(open("content.json", encoding="utf-8"))
    menu = json.load(open("menu.json", encoding="utf-8"))

    for lang, meta in LANGS.items():
        d = content[lang]
        prefix = "" if meta["dir"] == "" else "../"

        page = tpl
        page = page.replace("{{LANG}}", lang)
        page = page.replace("{{SITE}}", SITE)
        page = page.replace("{{A}}", prefix)
        page = page.replace("{{CANONICAL}}", url_for(lang))
        page = page.replace("{{OGLOCALE}}", meta["locale"])
        page = page.replace("{{HREFLANG}}", hreflang_block())
        page = page.replace("{{LANGSW}}", switcher(lang))
        page = page.replace("{{PEEK}}", peek_block(menu, lang, prefix))
        for key, val in d.items():
            page = page.replace("{{" + key + "}}", val)

        left = re.findall(r"\{\{[a-zA-Z0-9._]+\}\}", page)
        if left:
            raise SystemExit(f"[{lang}] не заменено: {sorted(set(left))}")

        out_dir = meta["dir"].rstrip("/")
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "index.html")
        open(path, "w", encoding="utf-8").write(page)
        print(f"  {path:20} {len(page)//1024} КБ")

    priced = sum(1 for i in menu["items"] if i.get("price") is not None)
    print(f"  блюд на витрине: {len(menu['items'])}, из них с ценой: {priced}")

    today = date.today().isoformat()
    urls = []
    for lang in LANGS:
        alts = "\n".join(
            f'      <xhtml:link rel="alternate" hreflang="{lg}" href="{url_for(lg)}"/>'
            for lg in LANGS
        )
        urls.append(
            f"""  <url>
    <loc>{url_for(lang)}</loc>
{alts}
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>{'1.0' if lang == DEFAULT else '0.9'}</priority>
  </url>"""
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    open("sitemap.xml", "w", encoding="utf-8").write(sitemap)
    print("  sitemap.xml")

    open("robots.txt", "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"
    )
    print("  robots.txt")


if __name__ == "__main__":
    print("Сборка:")
    build()
    print("Готово.")
