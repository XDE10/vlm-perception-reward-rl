"""Small compatibility shims across transformers 4.x and 5.x."""


def vision_model_class():
    """Auto class for image-text-to-text models (``AutoModelForVision2Seq`` was removed in transformers 5)."""
    import transformers

    for name in ("AutoModelForImageTextToText", "AutoModelForVision2Seq"):
        if hasattr(transformers, name):
            return getattr(transformers, name)
    raise ImportError("transformers provides neither AutoModelForImageTextToText nor AutoModelForVision2Seq")


__all__ = ["vision_model_class"]
