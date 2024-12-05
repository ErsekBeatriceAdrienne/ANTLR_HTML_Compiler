from antlr4 import *
import sys
import os

# Grammars elérési útvonal beállítása
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from grammars.HTMLLexer import HTMLLexer
from grammars.HTMLParser import HTMLParser
from grammars.HTMLParserListener import HTMLParserListener


class HTMLContentListener(HTMLParserListener):
    def __init__(self):
        self.titles = []
        self.headers = []

    def enterHtmlElement(self, ctx):
        # <title> elem feldolgozása
        if ctx.TAG_NAME(0) and ctx.TAG_NAME(0).getText() == "title":
            content = ctx.htmlContent()
            if content:
                self.titles.append(content.getText())

        # <h1> elem feldolgozása
        elif ctx.TAG_NAME(0) and ctx.TAG_NAME(0).getText() == "h1":
            content = ctx.htmlContent()
            if content:
                self.headers.append(content.getText())


def analyze_html_with_listener(file_path):
    # Ellenőrizzük, hogy a fájl létezik-e
    if not os.path.exists(file_path):
        print(f"Hiba: A fájl nem található: {file_path}")
        return

    # Fájl tartalmának beolvasása
    with open(file_path, 'r', encoding='utf-8') as file:
        html_code = file.read()

    # Tokenizálás és elemzés
    input_stream = InputStream(html_code)
    lexer = HTMLLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = HTMLParser(token_stream)

    # Parse fa generálása
    tree = parser.htmlDocument()

    # Listener inicializálása és feldolgozás
    listener = HTMLContentListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)

    # Eredmények kiírása
    print("Titles:", listener.titles)
    print("Headers (H1):", listener.headers)


def main():
    if len(sys.argv) < 2:
        print("Használat: python src/main.py <html_fájl_útvonal>")
        return

    file_path = sys.argv[1]
    analyze_html_with_listener(file_path)



if __name__ == "main":
    main()