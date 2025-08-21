import html5lib

fh = "test_for_html.html"


with open(fh, "rb") as f:
    document = html5lib.parse(f)
print(document)
