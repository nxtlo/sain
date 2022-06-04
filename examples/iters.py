"""An example on dealing with iterators."""

import dataclasses

import sain


@dataclasses.dataclass
class Person:
    name: str
    age: int


def create_people() -> sain.Iter[Person]:
    # Turn list into Iter[Person]
    return sain.into_iter(
        [
            Person("Alice", 21),
            Person("Bob", 25),
            Person("Charlie", 30),
        ]
    )


def normal_iter() -> None:
    people = create_people()

    # Normal iteration
    for person in people:
        print(person.name, person.age)

    # Elements go out of scope since they're generated lazily.
    print(people)  # <Iter()>


def filtered() -> None:
    people = create_people()

    # Filter by age and enumerate.
    for index, person in people.filter(lambda p: p.age >= 25).enumerate():
        print("+25", index, person.name, person.age)


def limited() -> None:
    # Limit to first 2 elements and map the name.
    people = create_people()

    for name in people.take(2).map(lambda p: p.name.title()):
        print("Limited to the first 2", name)


def discarded() -> None:
    people = create_people()

    # Discard people older than 25
    for person in people.discard(lambda p: p.age < 25):
        print("-25 Only", person)


def main() -> None:
    normal_iter()
    filtered()
    limited()
    discarded()


if __name__ == "__main__":
    main()
