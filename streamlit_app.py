import re, html as html_mod, pandas as pd, io, streamlit as st

st.set_page_config(page_title="Экстрактор студий → Excel", page_icon="📄")
st.title("Экстрактор студий → Excel")

file = st.file_uploader("Загрузите HTML/TXT", type=["html","htm","txt"])
dedup_mode = st.radio("Дедупликация", ["по паре (Студия, Адрес)", "только по Студии"])

def extract(text: str):
    blocks = re.split(r'<li\s+class="search-snippet-view">', text)
    rec = []
    for blk in blocks[1:]:
        blk = blk.split("</li>", 1)[0]
        m_title = re.search(
            r'<div\s+class="search-business-snippet-view__title"\s*>\s*(.*?)\s*</div>',
            blk, flags=re.S|re.I
        )
        m_addr  = re.search(
            r'<a[^>]*class="search-business-snippet-view__address"[^>]*>\s*(.*?)\s*</a>',
            blk, flags=re.S|re.I
        )
        if not (m_title and m_addr):
            continue
        clean = lambda s: html_mod.unescape(re.sub(r"<[^>]+>", " ", s)).strip()
        title, addr = clean(m_title.group(1)), clean(m_addr.group(1))
        if title and addr:
            rec.append({"Студия": title, "Адрес": addr})
    return pd.DataFrame(rec)

if file is not None:
    text = file.read().decode("utf-8", errors="ignore")
    df = extract(text)
    if dedup_mode == "только по Студии":
        df = df.drop_duplicates(subset=["Студия"])
    else:
        df = df.drop_duplicates(subset=["Студия","Адрес"])
    st.write(df)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    st.download_button(
        "Скачать studios.xlsx",
        data=buf,
        file_name="studios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
