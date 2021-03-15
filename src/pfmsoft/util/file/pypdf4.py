from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from PyPDF4 import PdfFileReader


@dataclass
class PageContent:
    page_number: int
    page_text: str


def get_page_content(
    file_path: Path,
    start_range: int = 0,
    end_range: int = -1,
    start_filter: Optional[Callable[[int, str], bool]] = None,
    end_filter: Optional[Callable[[int, str], bool]] = None,
    content_filter: Optional[Callable[[int, str], bool]] = None,
) -> List[PageContent]:
    """Get the text from a pdf file.

    Get the text from each page of a pdf file, with optional limits to page range, and flag filters for
    start, end, and page content. Returns a PageContent containing page_number and page_text.

    Arguments:
        file_path {Path} -- [description]

    Keyword Arguments:
        start_range {int} -- [description] (default: {0})
        end_range {int} -- [description] (default: {-1})
        start_filter {Optional[Callable[[int, str], bool]]} -- [description] (default: {None})
        end_filter {Optional[Callable[[int, str], bool]]} -- [description] (default: {None})
        content_filter {Optional[Callable[[int, str], bool]]} -- [description] (default: {None})

    Raises:
        ValueError: [description]
        ValueError: [description]

    Returns:
        List[PageContent] -- [description]
    """

    def pass_through_true(page_number: int, page_content: str):
        return True

    def pass_through_false(page_number: int, page_content: str):
        return False

    if start_filter is None:
        start_filter = pass_through_true
    if end_filter is None:
        end_filter = pass_through_false
    if content_filter is None:
        content_filter = pass_through_true

    retval: List[PageContent] = []
    start_flag = False

    with open(file_path, "rb") as f:
        read_pdf = PdfFileReader(f)
        number_of_pages = read_pdf.getNumPages()
        if number_of_pages is None:
            raise ValueError(f"No pages found for {file_path}")

        if end_range == -1 or end_range > number_of_pages:
            end_range = int(number_of_pages)
        if start_range > end_range:
            raise ValueError(
                f"{start_range} is bigger than {end_range}. Cannot count backwards."
            )

        for x in range(start_range, end_range):
            page = read_pdf.getPage(x)
            page_text = page.extractText()
            if not start_flag:
                if start_filter(x, page_text):
                    retval.append(PageContent(x, page_text))
                    start_flag = True
                    continue
                continue
            if end_filter(x, page_text):
                retval.append(PageContent(x, page_text))
                break
            if content_filter(x, page_text):
                retval.append(PageContent(x, page_text))
                continue
    return retval
