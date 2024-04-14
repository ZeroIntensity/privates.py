import inspect
from pathlib import Path
from types import FrameType as Frame

from .exceptions import FrameError

__all__ = ("get_back_frame",)


def get_back_frame() -> Frame:
    """Get the last frame outside of privates.py"""
    orig_frame = inspect.currentframe()

    if not orig_frame:
        raise FrameError("failed to get current frame")

    frame = orig_frame

    count = 0
    while (
        Path(frame.f_code.co_filename).parent
        == Path(orig_frame.f_code.co_filename).parent
    ):
        count += 1

        if not frame.f_back:
            raise FrameError(
                f"{frame} (nested {count} time(s) from current frame) has no f_back"  # noqa
            )

        frame = frame.f_back

    return frame
