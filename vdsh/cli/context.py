from dataclasses import dataclass
from pathlib import Path

from vdsh.cli.logger import Logger
from vdsh.core.iterator import BaseIterator, SequenceIterator
from vdsh.core.models.token import BaseToken
from vdsh.core.pipeline import CodeGenerator, Optimizer, Parser, Pipeline, Tokenizer, TypeChecker


@dataclass
class Context:
    verbose: bool
    data: str

    def create_token_iterator(self) -> BaseIterator[BaseToken]:
        return Tokenizer(char_iterator=SequenceIterator(self.data))

    def create_parser(self) -> Parser:
        return Parser(token_iterator=self.create_token_iterator())

    def create_pipeline(self) -> Pipeline:
        return Pipeline(
            parser=self.create_parser(),
            optimizer=Optimizer(),
            type_checker=TypeChecker(),
            code_generator=CodeGenerator(),
        )

    def create_logger(self) -> Logger:
        return Logger(verbose=self.verbose)


def create_context(verbose: bool, code: bool, src: str) -> Context:
    return Context(
        verbose=verbose,
        data=src if code else Path(src).read_text(),
    )
