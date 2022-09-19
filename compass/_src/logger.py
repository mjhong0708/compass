from datetime import datetime
from typing import Optional

import termcolor


def log(msg: str, level: str = "MAIN", filename: Optional[str] = None, append=True) -> None:
    """Simple logging function.
    Not for serious logging, just for pretty-printing the progress.

    Args:
        msg: Log message
        level: The level of task
        filename: Optional. If set, appends message to designated file.
    """
    curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_full = f"[{curr_time}] - {level}\t{msg}"

    # Print colored message to terminal
    msg_colored = termcolor.colored(f"[{curr_time}]", "green")
    msg_colored += f" - {termcolor.colored(level, 'blue')}"
    msg_colored += f"\t{msg}"
    print(msg_colored)

    # Append or write message to file.
    # Non-colored message is used.
    if filename is not None:
        mode = "a" if append else "w"
        with open(filename, mode) as f:
            f.write(msg_full + "\n")
