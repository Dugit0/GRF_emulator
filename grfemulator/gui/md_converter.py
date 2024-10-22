import mdtex2html


with open("help.md", encoding="utf-8") as f:
    text = f.read()

with open("help.html", "w", encoding="utf-8") as f:
    f.write(mdtex2html.convert(text))
