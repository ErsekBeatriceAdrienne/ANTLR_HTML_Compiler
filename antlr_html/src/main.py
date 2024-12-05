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
        self.open_tags = []  # Track open tags
        self.errors = []  # To store errors
        self.expected_tags = ['html', 'head', 'body']   # Track tags that are expected to be present
        self.seen_tags = []  # Keep track of tags we've seen

    def enterHtmlElement(self, ctx):
        tag_name = ctx.TAG_NAME(0).getText() if ctx.TAG_NAME(0) else None
        
        if tag_name:
            # Track opened tags with line number
            self.open_tags.append((tag_name.lower(), ctx.start.line))
            self.seen_tags.append(tag_name.lower())  # Record the tag as seen

            # Remove expected tag once it's found
            if tag_name.lower() in self.expected_tags:
                self.expected_tags.remove(tag_name.lower())

    def exitHtmlElement(self, ctx):
        tag_name = ctx.TAG_NAME(0).getText() if ctx.TAG_NAME(0) else None
        
        if tag_name:
            closing_tag_line = ctx.stop.line

            # Check if we are closing an open tag
            open_tag = next((t for t in self.open_tags if t[0] == tag_name.lower()), None)
            if open_tag:
                self.open_tags.remove(open_tag)
            else:
                self.errors.append(f"Error: Closing tag </{tag_name}> without an opening tag at line {closing_tag_line}. This could indicate an imbalance in the document structure.")

            # Check for unclosed tag (like <h1> instead of </h1>)
            if ctx.getText().startswith(f"<{tag_name}>") and not ctx.getText().endswith(f"</{tag_name}>"):
                self.errors.append(f"Error: Closing tag </{tag_name}> is missing the '/' at line {closing_tag_line}. This tag was not properly closed.")

    def endOfDocument(self):
        # Check for missing <html>, <body>, and <head> tags
        missing_tags = []
        if 'html' not in self.seen_tags:
            missing_tags.append("<html>")
        if 'head' not in self.seen_tags:
            missing_tags.append("<head>")
        if 'body' not in self.seen_tags:
            missing_tags.append("<body>")
        
        # Report any missing tags
        for tag in missing_tags:
            self.errors.append(f"Error: Missing {tag} tag in the document. This is a critical structural element that should be included at the top level.")
        
        # Check for unclosed tags at the end of the document
        if self.open_tags:
            for tag, line in self.open_tags:
                self.errors.append(f"Error: Unclosed <{tag}> tag at line {line}. This tag was opened but not properly closed.")

        # Output any errors found
        if self.errors:
            for error in self.errors:
                print(error)
        else:
            print("No errors found.")



def analyze_html_with_listener(file_path):
    if not os.path.exists(file_path):
        print(f"Hiba: A fájl nem található: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        html_code = file.read()

    input_stream = InputStream(html_code)
    lexer = HTMLLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = HTMLParser(token_stream)

    tree = parser.htmlDocument()

    listener = HTMLContentListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    
    # Manually call endOfDocument after the walk is completed
    listener.endOfDocument()


def main():
    if len(sys.argv) < 2:
        print("Használat: python src/main.py <html_fájl_útvonal>")
        return

    file_path = sys.argv[1]
    analyze_html_with_listener(file_path)

if __name__ == "__main__":
    main()
