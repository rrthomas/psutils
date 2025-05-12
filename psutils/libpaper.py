"""PSUtils libpaper interface.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import os
import re
import subprocess
from typing import Optional

from .types import Rectangle
from .warnings import die


# Get the size of the given paper, or the default paper if no argument given.
def paper(cmd: list[str], silent: bool = False) -> Optional[str]:
    cmd.insert(0, "paper")
    try:
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL if silent else None,
            text=True,
            env=dict(os.environ, LC_NUMERIC="C"),
        )
        return out.rstrip()
    except subprocess.CalledProcessError:
        return None
    except Exception:
        die("could not run `paper' command")


def get_paper_size(paper_name: Optional[str] = None) -> Optional[Rectangle]:
    if paper_name is None:
        paper_name = paper(["--no-size"])
    dimensions: Optional[str] = None
    if paper_name is not None:
        dimensions = paper(["--unit=pt", paper_name], True)
    if dimensions is None:
        return None
    m = re.search(" ([.0-9]+)x([.0-9]+) pt$", dimensions)
    assert m
    w, h = float(m[1]), float(m[2])
    return Rectangle(round(w), round(h))  # round dimensions to nearest point
