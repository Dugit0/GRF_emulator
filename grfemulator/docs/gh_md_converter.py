import gh_md_to_html
import argparse
parser = argparse.ArgumentParser(prog="Converter")
parser.add_argument("filename")

args = parser.parse_args()

with open(args.filename + ".md", encoding="utf-8") as f:
    text = f.read()

html_text = gh_md_to_html.core_converter.markdown(text)
# html_text = html_text.replace("<code>", "<pre><code>")
# html_text = html_text.replace("</code>", "<code></pre>")

with open(args.filename + ".html", "w", encoding="utf-8") as f:
    f.write(html_text)
