"""An example on dealing with iterators."""

import dataclasses

import sain


@dataclasses.dataclass
class Person:
    name: str
    age: int


def create_people() -> sain.Iter[Person]:
    # Create an iterator object that yields people.
    return sain.Iter(
        (
            Person("Alice", 21),
            Person("Bob", 25),
            Person("Charlie", 30),
        )
    )


def normal_iter() -> None:
    people = create_people()

    # Normal iteration
    for person in people:
        print(person.name, person.age)

    # Elements are free'd after iterating over them
    # since they're generated lazily.
    print(people.first().is_none())  # True


def filtered() -> None:
    people = create_people()

    # Filter by age and enumerate.
    table: dict[int, Person] = {}
    for index, person in people.filter(lambda p: p.age >= 25).enumerate():
        table[index] = person

    print(table)


def limited() -> None:
    # Limit to first 2 elements and map the name.
    people = create_people()

    for name in people.take(2).map(lambda p: p.name.title()):
        print("Limited to the first 2", name)


def main() -> None:
    normal_iter()
    filtered()
    limited()


if __name__ == "__main__":
    main()
