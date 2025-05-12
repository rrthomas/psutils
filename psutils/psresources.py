"""PSUtils utilities for dealing with PostScript Resources.

Copyright (c) Reuben Thomas 2023.
Released under the GPL version 3, or (at your option) any later version.
"""

import os
import re

from .warnings import die


# Resource extensions
def extn(ext: bytes) -> bytes:
    exts = {
        b"font": b".pfa",
        b"file": b".ps",
        b"procset": b".ps",
        b"pattern": b".pat",
        b"form": b".frm",
        b"encoding": b".enc",
    }
    return exts.get(ext, b"")


# Resource filename
def filename(*components: bytes) -> bytes:  # make filename for resource in 'components'
    name = b""
    for component in components:  # sanitise name
        c_str = component.decode()
        c_str = re.sub(r"[!()\$\#*&\\\|\`\'\"\~\{\}\[\]\<\>\?]", "", c_str)
        name += c_str.encode()
    name = os.path.basename(name)  # drop directories
    if name == b"":
        die(f'filename not found for resource {b" ".join(components).decode()}', 2)
    return name
