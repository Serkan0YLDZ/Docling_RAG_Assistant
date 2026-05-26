import logging
import os
import sys

from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.utils.accelerator_utils import decide_device

_log = logging.getLogger(__name__)

_ALIASES = {
    "gpu": AcceleratorDevice.AUTO.value,
    "auto": AcceleratorDevice.AUTO.value,
    "cpu": AcceleratorDevice.CPU.value,
    "cuda": AcceleratorDevice.CUDA.value,
    "mps": AcceleratorDevice.MPS.value,
    "xpu": AcceleratorDevice.XPU.value,
}


def resolve_docling_device() -> str:
    """Ortak .env DOCLING_DEVICE değerini Docling formatına çevirir."""
    raw = os.environ.get("DOCLING_DEVICE", "auto").strip().lower()
    if not raw:
        raw = "auto"
    device = _ALIASES.get(raw, raw)
    if device not in {d.value for d in AcceleratorDevice} and not (
        device.startswith("cuda")
    ):
        _log.warning("Geçersiz DOCLING_DEVICE=%s, auto kullanılıyor", raw)
        device = AcceleratorDevice.AUTO.value
    return device


def _allow_mps() -> bool:
    return os.environ.get("DOCLING_ALLOW_MPS", "").lower() in ("1", "true", "yes")


def _should_avoid_mps(resolved: str) -> bool:
    """Apple MPS + layout model float64 hatası için varsayılan olarak CPU."""
    if resolved != "mps":
        return False
    if _allow_mps():
        return False
    return True


def build_accelerator_options(num_threads: int | None = None) -> AcceleratorOptions:
    """Docling AcceleratorOptions; GPU yoksa veya MPS riskliyse CPU."""
    device = resolve_docling_device()
    os.environ["DOCLING_DEVICE"] = device
    threads = num_threads or int(os.environ.get("DOCLING_NUM_THREADS", "4"))
    options = AcceleratorOptions(device=device, num_threads=threads)
    resolved = decide_device(str(options.device))

    if _should_avoid_mps(resolved):
        _log.warning(
            "MPS layout modeli float64 desteklemiyor; DOCLING_DEVICE=cpu kullanılıyor. "
            "MPS için DOCLING_ALLOW_MPS=1 ve DOCLING_DEVICE=mps deneyin."
        )
        options = AcceleratorOptions(device=AcceleratorDevice.CPU.value, num_threads=threads)
        resolved = decide_device(AcceleratorDevice.CPU.value)
    elif resolved == "mps" and sys.platform == "darwin":
        _log.info("Docling MPS kullanılıyor (DOCLING_ALLOW_MPS=1)")

    _log.info("Docling istenen=%s çözümlenen=%s", device, resolved)
    return options
