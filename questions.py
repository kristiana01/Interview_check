"""Interview templates and problem tags used by Interview Check."""

ROLES = ["CEO", "CTO", "Developer", "Other"]

PROBLEM_TAGS = [
    ("no_owner", "No person responsible for testing"),
    ("no_cases", "No test cases or checklists"),
    ("no_automation", "No automated tests"),
    ("manual_regression", "Regression checked by hand"),
    ("limited_time", "Limited time for testing"),
    ("device_coverage", "Limited device or platform coverage"),
    ("single_reviewer", "Only one reviewer"),
    ("no_test_env", "No separate test environment"),
    ("no_analytics", "No usage analytics"),
    ("release_issues", "Problems found after release or in store review"),
]
TAG_LABELS = dict(PROBLEM_TAGS)

QUESTIONS = {
    "CEO": [
        "How is testing done at the company at the moment?",
        "Who takes part in testing the application, and has this changed over time?",
        "How do you decide that a new feature is ready to be released?",
        "Is there usually enough time to test new features before a release?",
        "What are the main difficulties when you develop the application quickly and want to be sure that it works well?",
        "How do user feedback and reported bugs help the team to improve the application?",
        "Have users or the app store review found problems that the team did not find itself?",
        "What do you know about how users behave in the app, and how do you get this information?",
        "What could be improved in the current testing process, and what limits these improvements?",
        "If you could change one thing in the testing process, what would it be?",
    ],
    "CTO": [
        "Can you describe how a new feature goes from a task to a release?",
        "When is the application tested, and who does the testing?",
        "How do developers check their work before it goes to review?",
        "What do you check during the code review? Does it include checking how the app behaves?",
        "How are bugs reported and tracked?",
        "How do you check that existing features still work after changes are made?",
        "How do you test the application on iOS and Android? Which devices are used?",
        "Do you use test cases, checklists or automated tests?",
        "What are the main difficulties when you check the code and prepare a release?",
        "What change would make testing easier or more effective for the team?",
    ],
    "Developer": [
        "How do you usually test a new feature that you have developed?",
        "Do you use test cases or checklists, or do you check the feature yourself without a list?",
        "How do you report bugs that you find?",
        "What do you do when someone reports a bug?",
        "How do you check that a bug is fixed and that other features still work?",
        "Do you test your changes on all platforms? What difficulties do you have?",
        "What is the most difficult part of testing your own work?",
        "How did the work change when the team changed its testing roles?",
        "What would make testing easier in your daily work?",
        "If you could change one thing in the testing process, what would it be?",
    ],
    "Other": [
        "How is testing done in your team at the moment?",
        "Who is responsible for testing?",
        "How do you decide that a feature is ready for release?",
        "What are the main problems in your testing process?",
        "What would you change first?",
    ],
}
