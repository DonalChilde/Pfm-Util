from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence

from pyparsing import ParseException, ParserElement


# pylint: disable=invalid-name
@dataclass
class ChunkParser:
    chunk_definition: ParserElement
    expected_next: List[str]
    result_handler: Any
    # result_handler: Callable[
    #     [dict, Optional[ParseResults], Optional[str], Optional["TextChunk"]], dict
    # ]


# @dataclass_json
@dataclass
class ParseMessage:
    category: str = ""
    message: str = ""
    text_chunk = Optional["TextChunk"]
    data: str = ""


@dataclass
class TextChunk:
    chunk_id: str = ""
    name: str = ""
    text_chunk: str = ""
    chunk_id_key: str = ""

    def __str__(self):
        return (
            f"[{self.chunk_id} - {self.name}] [{self.chunk_id_key}] {self.text_chunk}"
        )


# TODO consider taking chunk_id out of result handler signature, as it is duplicated inside chunk.
# TODO consider making the result handler an ABCclass, to guarantee signature of handler.
# TODO define schemes as subclass of ChunkParser. Make class of ChunkParser that represents
#   state, and assumes no parse, eg. Origin?
# TODO define parse framework, split from pyparsing. userdefine parser in subclasses.
# TODO allow custom chunker
# TODO pass definable look ahead chunks and look behind chunks to parser.


def advance_parse_position(line_id: str) -> bool:
    if line_id not in ["UNKNOWN", "BLANK"]:
        return True
    else:
        return False


class TextChunkParser:
    """
    parse scheme reserved keys: "ORIGIN","START","END","TERMINUS"
    parse context reserved keys: "PARSE_RESULT"
    """

    def __init__(
        self,
        parse_scheme: Dict[str, ChunkParser],
        check_parse_advance: Optional[Callable[[str], bool]] = None,
    ):
        if check_parse_advance:
            self.check_parse_advance = check_parse_advance
        else:
            self.check_parse_advance = self.advance_parse_position
        self.parse_scheme = parse_scheme

    def identify_chunks(
        self,
        chunks: Sequence[Sequence[TextChunk]],
        parse_context: Optional[Dict[str, Any]] = None,
    ) -> Sequence[Sequence[TextChunk]]:
        if not parse_context:
            parse_context = dict()
        parse_position = "ORIGIN"
        # parse_context = self.parse_scheme[parse_position].result_handler(
        #     parse_context, None, None, None
        # )
        for chunk_list in chunks:
            parse_position = "START"
            # parse_context = self.parse_scheme[parse_position].result_handler(
            #     parse_context, None, None, None
            # )
            for chunk in chunk_list:
                expected_keys = self.parse_scheme[parse_position].expected_next
                result = self.parse_attempt(expected_keys, chunk)
                if not result:
                    print(f"Broken: could not parse {chunk.text_chunk}")
                    # TODO better error handling and messaging
                    raise NotImplementedError
                chunk_id_key, parse_result = result
                chunk.chunk_id_key = chunk_id_key
                if self.check_parse_advance(chunk_id_key):
                    parse_position = chunk_id_key
                # parse_context = self.parse_scheme[chunk_id_key].result_handler(
                #     parse_context, parse_result, chunk_id_key, chunk
                # )
            parse_position = "END"
            # parse_context = self.parse_scheme[parse_position].result_handler(
            #     parse_context, None, None, None
            # )
        parse_position = "TERMINUS"
        # parse_context = self.parse_scheme[parse_position].result_handler(
        #     parse_context, None, None, None
        # )
        return chunks

    def parse_chunks(
        self,
        chunks: Sequence[Sequence[TextChunk]],
        parse_context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Identify chunks and pass them to the associated handler.
        there are four positional handlers to enable more fine grained
        handling of position related parsing.
        ORIGIN: Before any parsing is attempted.
        START: The beginning of a list of TextChunks, before parsing.
        END: The end of a list of TextChunks
        TERMINUS: After all parsing is complete.

        The parseContext dict is passed to each result handler, and can be used to
        track state, and contain objects derived from the parsed text.
        """
        if not parse_context:
            parse_context = dict()
        parse_position = "ORIGIN"
        parse_context = self.parse_scheme[parse_position].result_handler(
            parse_context, None, None, None
        )
        for chunk_list in chunks:
            parse_position = "START"
            parse_context = self.parse_scheme[parse_position].result_handler(
                parse_context, None, None, None
            )
            for chunk in chunk_list:
                expected_keys = self.parse_scheme[parse_position].expected_next
                result = self.parse_attempt(expected_keys, chunk)
                if not result:
                    print(f"Broken: could not parse {chunk.text_chunk}")
                    # TODO better error handling and messaging
                    raise NotImplementedError
                chunk_id_key, parse_result = result
                chunk.chunk_id_key = chunk_id_key
                if self.check_parse_advance(chunk_id_key):
                    parse_position = chunk_id_key
                parse_context = self.parse_scheme[chunk_id_key].result_handler(
                    parse_context, parse_result, chunk_id_key, chunk
                )
            parse_position = "END"
            parse_context = self.parse_scheme[parse_position].result_handler(
                parse_context, None, None, None
            )
        parse_position = "TERMINUS"
        parse_context = self.parse_scheme[parse_position].result_handler(
            parse_context, None, None, None
        )
        return parse_context  # type: ignore

    def parse_attempt(self, key_list: Sequence[str], text_chunk: TextChunk):
        for key in key_list:
            try:
                result = self.parse_scheme[key].chunk_definition.parseString(
                    text_chunk.text_chunk
                )
                return (key, result)
            except ParseException:
                continue
        return None

    def advance_parse_position(self, chunk_id_key: str) -> bool:
        return chunk_id_key not in ["UNKNOWN", "BLANK"]
