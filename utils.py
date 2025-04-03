# utils.py

from rich.markdown import Markdown
from rich.console import Console
console = Console()

class Display:
    def __init__(self, ):
        self.text = None

    def show( self, text, style: str= "bold blue" ):
        """ display text """
        console  = Console()
        md = Markdown(text)
        console.print( md, style=style)