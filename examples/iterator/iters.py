#
# * In this example, we demonstrate how to use the `sain` library to create a simple
# * iterator that yields messages with a text and an optional motto.

from __future__ import annotations

# to construct classes quickly.
import dataclasses

# import the option type to handle optional values.
from sain.option import Some, Option

# here you have the choice to choose between `Iterator` or `ExactSizeIterator`
# depending on whether you need to know the size of the iterator in advance.
from sain.iter import ExactSizeIterator, TrustedIter


@dataclasses.dataclass
class Message:
    content: str
    """The content of the message."""
    description: Option[str] = dataclasses.field(default=Some(None))
    """The description of the message, which is optional."""

    def is_complete(self) -> bool:
        """Check if the message is complete."""
        return self.description.is_some()


@dataclasses.dataclass
class MessageIterator(ExactSizeIterator[Message]):
    """A client that stores a set of `Message` objects."""

    messages: list[Message]
    """An array holding the messages."""

    def __next__(self) -> Message:
        # Check if we ran out of messages.
        if len(self.messages) == 0:
            raise StopIteration

        # remove and return the first message from the list.
        return self.messages.pop(0)

    # We need to define this if we're using `ExactSizeIterator`.
    # That's not the case for `Iterator` though.
    def __len__(self) -> int:
        return len(self.messages)


def main() -> None:
    # If you don't want to implement the iterator yourself,
    # you can use `TrustedIter` to create an iterator from an iterable.
    messages = [
        Message("Hello, world!", Some("Greeting")),
        Message("Goodbye, world!", Some("Farewell")),
        Message("Welcome back!"),
    ]
    it = TrustedIter(messages.copy())

    # be careful that `messages` is being mutated by the iterator,
    # because `.pop` is being called. So at the end of the iteration,
    # `messages` will be empty. Thats why we use `messages.copy()` in `it`.
    iterator = MessageIterator(messages)
    for msg in iterator:
        print(msg.content, msg.description)

    assert len(messages) == 0

    # use some adapters to perform operations on each message,
    # then collect the results.
    results: list[tuple[int, str]] = []
    (
        it
        # Check if the message is complete.
        .filter(Message.is_complete)
        # then map it to its contents.
        .map(lambda m: m.content)
        # then get each index of the message.
        .enumerate()
        # Now map it again into a (index, Message).
        .map(lambda args: (args[0], args[1]))
        # and collect the results into a mutable sequence.
        .collect_into(results)
    )
    for index, content in results:
        print(f"Message {index}: {content}")


if __name__ == "__main__":
    main()
