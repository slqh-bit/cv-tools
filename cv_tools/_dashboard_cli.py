"""
Console entry point for the Streamlit dashboard.

``streamlit run`` needs a path to a script, which an installed package does not
give the user an obvious way to find. This resolves ``dashboard.py`` inside the
installed package and hands it to Streamlit's own CLI, so ``cv-tools-dashboard``
works the same from a clone and from a wheel.

Arguments are passed straight through, so the usual Streamlit options still
apply:

    cv-tools-dashboard --server.address=0.0.0.0 --server.port=8502
"""

import sys
from pathlib import Path
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    try:
        from streamlit.web import cli as streamlit_cli
    except ImportError:
        print(
            'The dashboard needs Streamlit, which is an optional dependency.\n'
            '    pip install "cv-tools[dashboard]"',
            file=sys.stderr,
        )
        return 1

    script = Path(__file__).with_name('dashboard.py')
    if not script.is_file():                # pragma: no cover - broken install
        print(f'dashboard.py not found at {script}', file=sys.stderr)
        return 1

    # streamlit's CLI reads sys.argv rather than taking arguments.
    sys.argv = ['streamlit', 'run', str(script), *argv]
    return streamlit_cli.main()


if __name__ == '__main__':
    sys.exit(main())
