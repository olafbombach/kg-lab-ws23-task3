from dataclasses import dataclass
import polars as pl


@dataclass
class Token:
    """
    One of the outputs of the Tokenizer. (tbc)
    """
    token: tuple[str, str, float]


@dataclass
class TokenSet:
    """
    The complete output that is generated by the Tokenizer. (tbc)
    """
    tokens: set[Token]

    # maybe add some other properties
    def __post_init__(self):
        self.length: int = len(self.tokens)


@dataclass
class ProceedingsEvent:
    """
    The instance class of a Proceedings.com event. In this all information can be stored during one process run. (tbc)
    """
    input_info: pl.Series = None
    keywords: TokenSet


def main():
    event = ProceedingsEvent()
    print(event)


if __name__ == "__main__":
    main()
