"""
`evm t8n` runner.
"""

import json
import subprocess
from pathlib import Path
from typing import List, Mapping, Tuple, Union

JSONValue = Union[str, int, float, bool, None]
JSON = Union[JSONValue, Mapping[str, JSONValue], List[JSONValue]]


class TransitionTool:
    """
    Transition tool frontend.
    """

    binary: Path = Path("evm")

    def evaluate(
        self,
        alloc: Mapping[str, Mapping[str, str]],
        txs: List[JSON],
        env: Mapping[str, str],
    ) -> Tuple[JSON, JSON]:
        """
        Executes `evm t8n` with the specified arguments.
        """
        args = [
            self.binary,
            "--input.alloc=stdin",
            "--input.txs=stdin",
            "--input.env=stdin",
            "--output.result=stdout",
            "--output.alloc=stdout",
        ]
        stdin = {
            "alloc": alloc,
            "txs": txs,
            "env": env,
        }
        result = subprocess.run(args, input=str.encode(json.dumps(stdin)))

        if result.returncode != 0:
            pass

        output = json.loads(result.stdout)

        if "alloc" not in output or "result" not in output:
            pass

        return (output["alloc"], output["result"])
