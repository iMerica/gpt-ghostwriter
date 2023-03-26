import argparse
import logging
import asyncio
import os
import openai
import sys
from git import Repo
from functools import reduce
from itertools import chain

from gpt_ghostwriter import __version__

__author__ = "@iMerica"
__copyright__ = "Michael Martinez 2023"
__license__ = "MIT"

_logger = logging.getLogger(__name__)



class GPTGhostwriter:
    PROMPT = "Summarize the following code changes briefly"
    COMMIT_MSG_PROMPT = "In less than 50 characters, summarize a commit message about all of the following summaries."
    OPENAI_ORG = os.getenv("OPENAI_ORG_ID")
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    PROMPT_CUTOFF = 10000
    MODEL = "gpt-3.5-turbo"

    def __init__(self) -> None:
        self.repo = Repo('.')
        

    @property
    def diff(self):
        return self.repo.git.diff(
            self.repo.head.commit.tree,
            ignore_blank_lines=True,
            ignore_space_at_eol=True,
        )

    @staticmethod
    def parse_diff(diff):
        file_diffs = ["\ndiff" + file_diff for file_diff in diff.split("\ndiff")[1:]]
        chunked_file_diffs = []
        for file_diff in file_diffs:
            head, *chunks = file_diff.splitlines()
            chunks = ["\n@@" + chunk for chunk in reversed(chunks) if chunk.startswith("+") or chunk.startswith("-")]
            chunked_file_diffs.append((head, chunks))
        return chunked_file_diffs

    @staticmethod
    def assemble_diffs(parsed_diffs, cutoff):
        """
        Create multiple well-formatted diff strings, each being shorter than cutoff
        """
        def split_text(text):
            while text:
                if len(text) <= cutoff:
                    yield text
                    text = ""
                else:
                    yield text[:cutoff]
                    text = text[cutoff:]

        def format_diffs(head, chunks):
            text = reduce(lambda x, y: x + "\n" + y, chain([head], chunks))
            return list(split_text(text))

        return reduce(
            lambda acc, x: acc + format_diffs(x[0], x[1]),
            parsed_diffs,
            [""]
        )

    async def summarize(self, diff):
        return await self.fetch_commit_message(
            self.PROMPT + "\n\n" + diff + "\n\n"
        )

    async def create_title(self, summaries):
        return await self.fetch_commit_message(
            self.COMMIT_MSG_PROMPT + "\n\n" + summaries + "\n\n"
        )

    
    async def fetch_commit_message(self, prompt):
        completion_resp = await openai.ChatCompletion.acreate(
            model=self.MODEL,
            messages=[
                {"role": "user", "content": prompt[: self.PROMPT_CUTOFF + 100]}
            ],
            max_tokens=128,
        )
        return completion_resp.choices[0].message.content.strip()

    async def generate_commit_message(self):
        diff = self.diff
        if not diff:
            return "Fix whitespace"

        assembled_diffs = self.assemble_diffs(self.parse_diff(diff), self.PROMPT_CUTOFF)
        if not assembled_diffs:
            return "No changes"
        summary_tasks = [asyncio.create_task(self.summarize(diff)) for diff in assembled_diffs]
        summaries = await asyncio.gather(*summary_tasks)
        return await self.create_title("\n".join(summaries))

    async def main(self):
        message = await self.generate_commit_message()
        print(message)


def main():
    gpt = GPTGhostwriter()
    asyncio.run(gpt.main())

if __name__ == "__main__":
    main()
