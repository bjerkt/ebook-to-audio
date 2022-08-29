from ebooklib import epub


def process_file_list(file_list):
    # {book_title, [chap1,...,chapn]}
    books = {}
    for book_file in file_list:
        book = epub.read_epub(book_file.__str__())
        # Remove spaces from book title
        book_title = book.title.replace(" ", "_")
        # Drop any other weird characters
        book_title = "".join(c for c in book_title if (c.isalnum() or c in "_-"))
        book_chapters = []
        # Spine gives "proper" order of documents. Gives id found in items list
        all_docs = [book.get_item_with_id(x[0]) for x in book.spine]
        for item in all_docs:
            print(item.id)
            book_chapters.append(item.get_content())
        books[book_title] = book_chapters
    return books
