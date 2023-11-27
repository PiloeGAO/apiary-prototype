"""Utility functions."""
import re


def split_text(text, sep=" ,;"):
    """Separate a text using a some characters.

    Args:
        text (str): Test to split.
        sep (str, optional): Split characters. Defaults to " ,;".

    Returns:
        list[str]: Text elements.
    """
    return re.split(f"[{sep}]", text)


def compute_framerange_chunks(start, end, size):
    """Get the frame range from a chunk size.

    Args:
        start (int): Start frame.
        end (int): End frame.
        size (int): Chunk size.

    Yields:
        list[int]: Frames inside of the chunk range.
    """
    for start_frame in range(start, end, size):
        end_frame = start_frame + size
        if end_frame >= end:
            end_frame = end + 1
        yield list(range(start_frame, end_frame))
