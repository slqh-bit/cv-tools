"""
Pipeline Engine - Manages ordered filter chains with undo/redo, presets, and reporting.
"""

import json
import copy
from typing import List, Dict, Any, Optional, Callable, Sequence, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

import numpy as np


@dataclass
class FilterStep:
    """Represents a single filter application in the chain."""
    name: str
    module: str
    params: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterStep':
        return cls(**data)


class Pipeline:
    """
    Filter chain pipeline with undo/redo, presets, and report generation.
    Mirrors Amped FIVE's chain-based workflow.
    """

    def __init__(self, original_image: np.ndarray):
        self._original = original_image.copy()
        self._current = original_image.copy()

        # History stacks for undo/redo
        self._history: List[Tuple[np.ndarray, FilterStep]] = []
        self._redo_stack: List[Tuple[np.ndarray, FilterStep]] = []

        # Chain of applied filters
        self._chain: List[FilterStep] = []

    @property
    def original(self) -> np.ndarray:
        return self._original.copy()

    @property
    def current(self) -> np.ndarray:
        return self._current.copy()

    @property
    def chain(self) -> List[FilterStep]:
        """Return the current filter chain."""
        return self._chain.copy()

    @property
    def can_undo(self) -> bool:
        """Whether there is a step to undo, for greying out a control."""
        return bool(self._history)

    @property
    def can_redo(self) -> bool:
        """Whether there is an undone step to redo, for greying out a control."""
        return bool(self._redo_stack)

    def apply(self, filter_fn: Callable, name: str, module: str, params: Dict[str, Any]) -> np.ndarray:
        """
        Apply a filter function and record it in the chain.

        Args:
            filter_fn: Function that takes (image, **params) and returns processed image
            name: Human-readable filter name
            module: Module path for the filter
            params: Parameters passed to the filter

        Returns:
            Processed image
        """
        # Save current state for undo
        self._history.append((self._current.copy(), FilterStep(name, module, params)))
        self._redo_stack.clear()  # Clear redo on new action

        # Apply filter
        try:
            result = filter_fn(self._current, **params)
            if not isinstance(result, np.ndarray):
                raise TypeError(f"Filter '{name}' must return a numpy array")
            self._current = result
            self._chain.append(FilterStep(name, module, params))
            return self._current.copy()
        except Exception as e:
            # Rollback on error
            self._history.pop()
            raise RuntimeError(f"Filter '{name}' failed: {e}") from e

    def undo(self) -> Optional[np.ndarray]:
        """Undo last filter application."""
        if not self._history:
            return None

        prev_state, step = self._history.pop()
        self._redo_stack.append((self._current.copy(), step))
        self._current = prev_state
        self._chain.pop()
        return self._current.copy()

    def redo(self) -> Optional[np.ndarray]:
        """Redo last undone filter."""
        if not self._redo_stack:
            return None

        next_state, step = self._redo_stack.pop()
        self._history.append((self._current.copy(), step))
        self._current = next_state
        self._chain.append(step)
        return self._current.copy()

    def reset(self) -> np.ndarray:
        """Reset to original image, clearing all filters."""
        self._current = self._original.copy()
        self._history.clear()
        self._redo_stack.clear()
        self._chain.clear()
        return self._current.copy()

    def compare(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return (original, current) for side-by-side comparison."""
        return self._original.copy(), self._current.copy()

    # ---- Preset System ----

    def save_preset(self, path: str, name: str = "", description: str = "") -> None:
        """Save current filter chain as a JSON preset."""
        preset = {
            'name': name or f"Preset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'description': description,
            'created_at': datetime.now().isoformat(),
            'filters': [step.to_dict() for step in self._chain],
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(preset, f, indent=2, ensure_ascii=False)

    def load_preset(self, path: str) -> Dict[str, Any]:
        """Load a preset file. Returns the preset dict (does not auto-apply)."""
        with open(path, 'r', encoding='utf-8') as f:
            preset = json.load(f)
        return preset

    def replace_chain(
        self,
        chain: Sequence[FilterStep],
        resolver: Callable[[str], Callable[..., np.ndarray]],
    ) -> np.ndarray:
        """
        Replace the entire chain and re-process from the original image.

        Use this to load a preset over an existing pipeline, or to reorder or
        drop steps: rebuild the list you want and pass it in.

        The pipeline cannot look filter functions up itself - that would make
        this module depend on the filters package it sits underneath - so the
        caller supplies a resolver. ``filters.registry.filter_function`` is one
        for every registered filter.

        Args:
            chain: Steps to apply, in order
            resolver: Maps a step's ``name`` to the function implementing it

        Returns:
            The reprocessed image

        Raises:
            KeyError: If the resolver does not recognise a step's name
            RuntimeError: If a filter fails

        On any failure the pipeline is left exactly as it was, so a chain that
        cannot be rebuilt never replaces one that works.

        Example:
            >>> from src.filters import filter_function
            >>> preset = pipeline.load_preset('plate.json')
            >>> steps = [FilterStep.from_dict(s) for s in preset['filters']]
            >>> pipeline.replace_chain(steps, filter_function)
        """
        snapshot = (
            self._current.copy(),
            list(self._chain),
            list(self._history),
            list(self._redo_stack),
        )

        try:
            self.reset()
            for step in chain:
                self.apply(resolver(step.name), step.name, step.module, step.params)
        except Exception:
            self._current, self._chain, self._history, self._redo_stack = snapshot
            raise

        return self._current.copy()

    # ---- Reporting ----

    def generate_report(self) -> Dict[str, Any]:
        """Generate a report of all applied filters."""
        original_shape = self._original.shape
        current_shape = self._current.shape

        return {
            'generated_at': datetime.now().isoformat(),
            'original_image': {
                'shape': original_shape,
                'dtype': str(self._original.dtype),
            },
            'current_image': {
                'shape': current_shape,
                'dtype': str(self._current.dtype),
            },
            'filter_count': len(self._chain),
            'filters': [step.to_dict() for step in self._chain],
        }

    def __len__(self) -> int:
        return len(self._chain)

    def __repr__(self) -> str:
        steps = ', '.join(s.name for s in self._chain) or 'empty'
        return f"Pipeline({len(self._chain)} steps: {steps})"
