from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup

FILES_LOCATION = "unused for now, will define folder that contains many epubs"


def parse_html(doc_string):
    soup = BeautifulSoup(doc_string, "html.parser")
    text = [paragraph.get_text() for paragraph in soup.find_all("p")]
    return " ".join(text)


def main():
    pth = Path(".")
    book_files = [x.name for x in pth.glob("*.epub")]
    for book_file in book_files:
        book = epub.read_epub(book_file)
        # Spine gives "proper" order of documents. Gives id found in items list
        all_docs = [book.get_item_with_id(x[0]) for x in book.spine]
        for item in all_docs:
            # Determining chapters and breaks is a difficult problem. EPUB formatting
            # is not standardized, and so there will be books out there that just
            # don't look like we expect. We do our best.
            # See https://cran.r-project.org/web/packages/epubr/vignettes/epubr.html
            section_html = item.get_content()
            # parse_html only pulls text between <p> tags - presumably only
            # chapter text.
            text = parse_html(section_html)


if __name__ == "__main__":
    main()
