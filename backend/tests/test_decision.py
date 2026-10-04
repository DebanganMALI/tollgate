from app.policy.models import Decision, Verdict, Violation


def v(severity):
    return Violation(rule="r", message="m", severity=severity)


def test_no_violations_allows():
    assert Decision.from_violations([]).verdict is Verdict.ALLOW


def test_review_only():
    assert Decision.from_violations([v(Verdict.REVIEW)]).verdict is Verdict.REVIEW


def test_deny_beats_review():
    d = Decision.from_violations([v(Verdict.REVIEW), v(Verdict.DENY)])
    assert d.verdict is Verdict.DENY
    assert len(d.violations) == 2
