from langchain_text_splitters import RecursiveCharacterTextSplitter


def smart_chunk(text: str) -> list[str]:
    """
    In here used token-base chunking, by using ".from_tiktoken_encoder" otherwise it get character base chunking if use this plain "RecursiveCharacterTextSplitter"
    """
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name = "cl100k_base",
        chunk_size = 512,
        chunk_overlap = 75,
        separators = [
            "\n\n",
            "\n",
            ".",
            " ",
            ""
        ]
    )

    chunk = splitter.split_text(text)
    
    return chunk