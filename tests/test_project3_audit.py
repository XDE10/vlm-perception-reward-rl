import io
import pytest

# Project 3 is an optional CPU audit module with its own pinned dependencies.
# The training-only venv may omit image/parquet tooling; do not break collection.
pytest.importorskip('PIL', reason='Install requirements-project3-cpu.txt in a dedicated audit venv')
pytest.importorskip('pyarrow', reason='Install requirements-project3-cpu.txt in a dedicated audit venv')
from PIL import Image
from src.data.project3_audit import image_hash, norm, question_forms


def test_pixels_ignore_png_encoding_but_preserve_shape():
    image=Image.new('RGB',(2,3),'red')
    a,b=io.BytesIO(),io.BytesIO()
    image.save(a,format='PNG',compress_level=0)
    image.save(b,format='PNG',compress_level=9)
    assert a.getvalue()!=b.getvalue()
    assert image_hash(a.getvalue())==image_hash(b.getvalue())
    c=io.BytesIO()
    Image.new('RGB',(3,2),'red').save(c,format='PNG')
    assert image_hash(a.getvalue())!=image_hash(c.getvalue())


def test_question_normalization_does_not_remove_mathematical_symbols():
    assert norm('<image> Find $x = 2$.')==norm('find $x=2$.')
    assert norm('Find x+2')!=norm('Find x-2')


def test_official_annotated_question_is_supported_without_row_guessing():
    record={'original_data':{'problem_text':'Find x.', 'compact_text':'Find x.',
                             'annotat_text':'Find $x$.'}}
    assert norm('<image>Find $x$.').rstrip('.') in question_forms(record).values()
    assert norm('Find $y$.').rstrip('.') not in question_forms(record).values()
