import os
import pytest

from mist.action_run import execute_from_text

EXAMPLE_FILE = "filterDict.mist"

@pytest.mark.asyncio
async def test_filterDict(examples_path):
    with open(os.path.join(examples_path, EXAMPLE_FILE), "r") as f:
        content = f.read()
    
    console = await execute_from_text(content)
    assert """{'a': 1, 'b': 2}
{'aa': 1, 'b': 2}
{'aa': 1, 'bb': 2}\n""" == console
