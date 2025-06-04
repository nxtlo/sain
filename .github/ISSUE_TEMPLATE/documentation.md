name: Documentation problem
description: Create a report for a documentation problem.
labels: ["C-documentation"]
body:
  - type: markdown
    attributes:
      value: |
        Thank you for finding a documentation problem!

        Documentation problems might be grammatical issues, typos, or unclear wording, please provide details regarding the documentation including where it is present.

  - type: textarea
    id: location
    attributes:
      label: Location
    validations:
      required: true 

  - type: textarea
    id: summary
    attributes:
      label: Summary
    validations:
      required: true 