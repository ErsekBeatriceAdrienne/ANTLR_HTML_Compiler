from antlr4 import *
import sys
import os
# Grammars elérési útvonal beállítása
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../grammars')))
from antlr4.error.ErrorListener import ErrorListener
from grammars.HTMLParser import HTMLParser as ANTLRHTMLParser
from grammars.HTMLLexer import HTMLLexer
from grammars.HTMLParserListener import HTMLParserListener


class HTMLParseErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()

    def syntaxError(self, recognizer, symbol, line, column, msg, e):
        print(f"Hiba: {msg} a {line}. sor {column}. oszlopában.")

class HTMLContentListener(HTMLParserListener):
    def __init__(self):
        self.titles = []
        self.headers = []

    def enterHtmlElement(self, ctx):
        # `<title>` elem feldolgozása
        if ctx.TAG_NAME(0) and ctx.TAG_NAME(0).getText() == "title":
            content = ctx.htmlContent()
            if content:
                self.titles.append(content.getText())

        # `<h1>` elem feldolgozása
        elif ctx.TAG_NAME(0) and ctx.TAG_NAME(0).getText() == "h1":
            content = ctx.htmlContent()
            if content:
                self.headers.append(content.getText())

def validate_html(html_code):
    """
    Validates HTML syntax. Returns True if valid, False otherwise.
    """
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.has_error = False

        def handle_starttag(self, tag, attrs):
            pass  # Handle start tags if needed

        def handle_endtag(self, tag):
            pass  # Handle end tags if needed

        def handle_data(self, data):
            pass  # Handle data within tags if needed

        def error(self, message):
            self.has_error = True
            raise Exception(message)

    parser = MyHTMLParser()
    try:
        parser.feed(html_code)
        return not parser.has_error
    except Exception as e:
        print(f"HTML validation error: {e}")
        return False

def analyze_html_with_listener(file_path):
    # Ellenőrizzük, hogy a fájl létezik-e
    if not os.path.exists(file_path):
        print(f"Hiba: A fájl nem található: {file_path}")
        return

    # Fájl tartalmának beolvasása
    with open(file_path, 'r', encoding='utf-8') as file:
        html_code = file.read()

    # HTML validálása
    if not validate_html(html_code):
        print("A HTML kód hibás. Elemzés leállítva.")
        return

    # Tokenizálás és elemzés
    input_stream = InputStream(html_code)
    lexer = HTMLLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = HTMLParser(token_stream)

    # Add the custom error listener
    parser.removeErrorListeners()
    parser.addErrorListener(HTMLParseErrorListener())

    # Parse fa generálása
    try:
        tree = parser.htmlDocument()
    except Exception as e:
        print(f"Hiba történt a HTML elemzés közben: {str(e)}")
        return

    # Listener inicializálása és feldolgozás
    listener = HTMLContentListener()
    walker = ParseTreeWalker()
    try:
        walker.walk(listener, tree)  # Sétálunk a parse fában
    except Exception as e:
        print("Hiba történt a parse tree bejárása során:", str(e))

    # Eredmények kiírása
    print("Titles:", listener.titles)
    print("Headers (H1):", listener.headers)

def main():
    if len(sys.argv) < 2:
        print("Használat: python src/main.py <html_fájl_útvonal>")
        return

    file_path = sys.argv[1]
    analyze_html_with_listener(file_path)

if __name__ == "__main__":
    main()

    '''További elemek: A enterHtmlElement metódusban bármilyen HTML tag feldolgozható, csak ellenőrizni kell a TAG_NAME(0) értékét.
Hibakezelés: Ha a HTML nem teljesen jól formázott, gondoskodj megfelelő hibakezelésről a grammatikában vagy a sétálóban.
Több szintű struktúrák: Ha mélyebbre szeretnél ásni, például <div>-eken belüli <h1> elemeket szeretnél feldolgozni, bővítsd a logikát.'''
