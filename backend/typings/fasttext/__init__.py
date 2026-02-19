# typings/fasttext/__init__.pyi
from typing import List, Tuple, Union

class FastText:
    def predict(
        self,
        text: Union[str, List[str]],
        k: int = 1,
        threshold: float = 0.0,
        on_unicode_error: str = "strict"
    ) -> Tuple[List[List[str]], List[List[float]]]: ...

def load_model(path: str, label_prefix: str = "__label__") -> FastText: ...
