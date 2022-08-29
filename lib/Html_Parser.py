from bs4 import BeautifulSoup


def parse_html(doc_string):
    soup = BeautifulSoup(doc_string, "html.parser")
    text = [paragraph.get_text() for paragraph in soup.find_all("p")]
    sec_list = []
    curr_sec = ""
    for p in text:
        if len(curr_sec) + len(p) < 4500:
            curr_sec += p + " "
        else:
            sec_list.append(curr_sec)
            curr_sec = ""
    if len(sec_list) == 0 and len(curr_sec) > 0:
        sec_list.append(curr_sec)
    return sec_list
