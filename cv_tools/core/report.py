"""
Report Generator - Creates forensic-style processing reports.

Markdown and JSON are written directly. PDF is rendered through matplotlib,
which is already a dependency, so producing a court-presentable report needs no
extra install.
"""

import json
import hashlib
import textwrap
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np

# A4 in inches, and the text layout that fits it
_PAGE_SIZE = (8.27, 11.69)
_LEFT_MARGIN = 0.09
_TOP = 0.95
_BOTTOM = 0.06

_STYLES = {
    #        size, weight,   family,      line height, wrap width
    'title': (16, 'bold', 'sans-serif', 0.034, 60),
    'heading': (12, 'bold', 'sans-serif', 0.028, 78),
    'body': (9, 'normal', 'sans-serif', 0.019, 100),
    'mono': (8, 'normal', 'monospace', 0.018, 95),
    'spacer': (9, 'normal', 'sans-serif', 0.012, 100),
}


class ReportGenerator:
    """Generate scientific reports of image processing chains."""

    def __init__(
        self,
        pipeline_report: Dict[str, Any],
        source_metadata: Dict[str, Any],
        describe: Optional[Callable[[str], str]] = None,
    ):
        """
        Args:
            pipeline_report: As returned by ``core.pipeline.Pipeline.generate_report``
            source_metadata: Loader metadata for the source file
            describe: Maps a step's ``name`` to a plain-language description of
                what the filter does. A report is read by someone who is not an
                image analyst, so a name and a parameter list do not tell them
                what was done. This module cannot look descriptions up itself -
                that would make ``core`` depend on the filters package it sits
                underneath - so the caller supplies a resolver, exactly as
                ``Pipeline.replace_chain`` takes one.
                ``filters.registry.filter_description`` is one for every
                registered filter. Omit it and the reports read as before.
        """
        self.pipeline_report = pipeline_report
        self.source_metadata = source_metadata
        self.describe = describe

    def _description(self, step: Dict[str, Any]) -> str:
        """Return the description for a step, or '' if there is none to give."""
        if self.describe is None:
            return ''
        return self.describe(step['name']) or ''

    def _alignment(self) -> Optional[Dict[str, Any]]:
        """The frame-alignment record, if the source was a stabilised stack."""
        alignment = self.source_metadata.get('alignment')
        return alignment if isinstance(alignment, dict) else None

    def _alignment_summary(self) -> str:
        """One sentence on what the alignment did."""
        alignment = self._alignment() or {}
        return (
            f"Aligned {alignment.get('aligned', 0)} of "
            f"{alignment.get('frames', 0)} frames with the "
            f"{alignment.get('model', '?')} motion model. Largest motion "
            f"{alignment.get('max_shift_pixels', 0)} px, mean confidence "
            f"{alignment.get('mean_confidence', 0):.2f}."
        )

    def _alignment_rows(self) -> List[Tuple[str, str, str, str, str]]:
        """Per-frame alignment as (frame, method, confidence, shift, note)."""
        alignment = self._alignment()
        if alignment is None:
            return []

        rows = []
        for record in alignment.get('per_frame', []):
            shift = record.get('shift', [0, 0])
            rows.append((
                str(record.get('index', '?')),
                str(record.get('method', '?')),
                f"{record.get('confidence', 0):.3f}",
                f"{shift[0]:+.2f}, {shift[1]:+.2f}",
                str(record.get('note', '')),
            ))
        return rows

    def to_dict(self) -> Dict[str, Any]:
        """Return full report as dictionary."""
        return {
            'report_type': 'Image Processing Chain Report',
            'generated_at': datetime.now().isoformat(),
            'source_file': self.source_metadata,
            'processing': self.pipeline_report,
        }

    def to_markdown(self) -> str:
        """Generate Markdown report (similar to Amped FIVE reports)."""
        lines = [
            "# Image Processing Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Source File",
            "",
        ]

        for key, value in self.source_metadata.items():
            # Rendered as its own section below: dumped inline it is a wall of
            # matrices, and this is a document someone has to read
            if key == 'alignment' and self._alignment() is not None:
                continue
            lines.append(f"- **{key}:** {value}")

        if self._alignment() is not None:
            lines.extend([
                "",
                "## Frame Alignment",
                "",
                self._alignment_summary(),
                "",
                "A frame that could not be matched is left out rather than "
                "warped on a guess.",
                "",
                "| Frame | Method | Confidence | Shift (x, y) | Note |",
                "|---|---|---|---|---|",
            ])
            for frame, method, confidence, shift, note in self._alignment_rows():
                lines.append(
                    f"| {frame} | {method} | {confidence} | {shift} | {note} |")

        lines.extend([
            "",
            "## Processing Chain",
            "",
            f"Total filters applied: **{self.pipeline_report.get('filter_count', 0)}**",
            "",
        ])

        for i, step in enumerate(self.pipeline_report.get('filters', []), 1):
            lines.append(f"### Step {i}: {step['name']}")
            description = self._description(step)
            if description:
                lines.extend([description, ""])
            lines.extend([
                f"- **Module:** `{step['module']}`",
                f"- **Timestamp:** {step['timestamp']}",
                "- **Parameters:**",
            ])
            for param_key, param_val in step.get('params', {}).items():
                lines.append(f"  - `{param_key}`: {param_val}")
            lines.append("")

        lines.extend([
            "## Output",
            "",
            f"- **Final shape:** {self.pipeline_report.get('current_image', {}).get('shape')}",
            f"- **Data type:** {self.pipeline_report.get('current_image', {}).get('dtype')}",
            "",
            "---",
            "*Report generated by cv-tools*",
        ])

        return '\n'.join(lines)

    def _styled_lines(self) -> List[Tuple[str, str]]:
        """
        Build the report as (text, style) pairs for the PDF renderer.

        Kept separate from ``to_markdown`` so the PDF is not littered with
        asterisks and backticks that only mean something to a Markdown reader.
        """
        lines: List[Tuple[str, str]] = [
            ('Image Processing Report', 'title'),
            (f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'body'),
            ('', 'spacer'),
            ('Source File', 'heading'),
        ]

        for key, value in self.source_metadata.items():
            if key == 'alignment' and self._alignment() is not None:
                continue        # its own section below
            if key == 'exif' and isinstance(value, dict):
                lines.append(('exif:', 'body'))
                for tag, tag_value in value.items():
                    lines.append((f"    {tag}: {tag_value}", 'mono'))
            elif key == 'sha256':
                # Hashes go in monospace so they can be checked character by
                # character against the source file
                lines.append((f"{key}:", 'body'))
                lines.append((f"    {value}", 'mono'))
            else:
                lines.append((f"{key}: {value}", 'body'))

        if self._alignment() is not None:
            lines.extend([
                ('', 'spacer'),
                ('Frame Alignment', 'heading'),
                (self._alignment_summary(), 'body'),
                ('A frame that could not be matched is left out rather than '
                 'warped on a guess.', 'body'),
                (f"{'frame':>5}  {'method':<14}{'conf':>6}  "
                 f"{'shift (x, y)':<16}note", 'mono'),
            ])
            for frame, method, confidence, shift, note in self._alignment_rows():
                lines.append((f"{frame:>5}  {method:<14}{confidence:>6}  "
                              f"{shift:<16}{note}", 'mono'))

        lines.extend([
            ('', 'spacer'),
            ('Processing Chain', 'heading'),
            (f"Total filters applied: {self.pipeline_report.get('filter_count', 0)}", 'body'),
            ('', 'spacer'),
        ])

        for index, step in enumerate(self.pipeline_report.get('filters', []), 1):
            lines.append((f"Step {index}: {step['name']}", 'heading'))
            description = self._description(step)
            if description:
                lines.append((description, 'body'))
            lines.append((f"Module: {step['module']}", 'body'))
            lines.append((f"Timestamp: {step['timestamp']}", 'body'))
            params = step.get('params', {})
            if params:
                lines.append(('Parameters:', 'body'))
                for param_key, param_value in params.items():
                    lines.append((f"    {param_key} = {param_value}", 'mono'))
            else:
                lines.append(('Parameters: defaults', 'body'))
            lines.append(('', 'spacer'))

        current = self.pipeline_report.get('current_image', {})
        lines.extend([
            ('Output', 'heading'),
            (f"Final shape: {current.get('shape')}", 'body'),
            (f"Data type: {current.get('dtype')}", 'body'),
            ('', 'spacer'),
            ('Report generated by cv-tools', 'body'),
        ])

        return lines

    def to_pdf(self, path: str) -> None:
        """
        Render the report as a paginated PDF.

        Args:
            path: Destination file

        Raises:
            RuntimeError: If matplotlib is unavailable
        """
        try:
            import matplotlib
            # Non-interactive backend: this runs headless and must never try to
            # open a window
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages
        except ImportError as exc:
            raise RuntimeError(
                f"PDF export requires matplotlib: {exc}"
            ) from exc

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with PdfPages(str(path)) as pdf:
            figure = plt.figure(figsize=_PAGE_SIZE)
            y = _TOP

            for text, style in self._styled_lines():
                size, weight, family, line_height, wrap_width = _STYLES[style]

                # Long paths and hashes must wrap rather than run off the page
                segments = textwrap.wrap(text, wrap_width) if text else ['']
                for segment in segments:
                    if y < _BOTTOM:
                        pdf.savefig(figure)
                        plt.close(figure)
                        figure = plt.figure(figsize=_PAGE_SIZE)
                        y = _TOP

                    if segment:
                        figure.text(_LEFT_MARGIN, y, segment, fontsize=size,
                                    fontweight=weight, family=family,
                                    verticalalignment='top')
                    y -= line_height

            pdf.savefig(figure)
            plt.close(figure)

    def save(self, path: str, format: str = 'markdown') -> None:
        """
        Save the report.

        Args:
            path: Destination file; the extension is corrected to match
            format: 'markdown' (or 'md'), 'json', or 'pdf'

        Raises:
            ValueError: If the format is not recognised
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fmt = format.lower()

        if fmt == 'pdf':
            self.to_pdf(path.with_suffix('.pdf'))
            return

        if fmt in ('md', 'markdown'):
            content = self.to_markdown()
            path = path.with_suffix('.md')
        elif fmt == 'json':
            content = json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
            path = path.with_suffix('.json')
        else:
            raise ValueError(f"Unknown format: {format}")

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


def hash_image(image: np.ndarray) -> str:
    """Compute SHA-256 hash of image data."""
    return hashlib.sha256(image.tobytes()).hexdigest()
