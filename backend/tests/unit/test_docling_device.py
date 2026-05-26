import os

import pytest

from app.infrastructure.docling_device import build_accelerator_options, resolve_docling_device


def test_gpu_alias_maps_to_auto(monkeypatch):
    monkeypatch.setenv("DOCLING_DEVICE", "gpu")
    assert resolve_docling_device() == "auto"


def test_cpu_explicit(monkeypatch):
    monkeypatch.setenv("DOCLING_DEVICE", "cpu")
    assert resolve_docling_device() == "cpu"


def test_invalid_falls_back_to_auto(monkeypatch):
    monkeypatch.setenv("DOCLING_DEVICE", "invalid-device")
    assert resolve_docling_device() == "auto"


def test_build_accelerator_options_resolves_device(monkeypatch):
    monkeypatch.setenv("DOCLING_DEVICE", "cpu")
    options = build_accelerator_options(num_threads=2)
    assert options.num_threads == 2
    assert str(options.device) == "cpu"
