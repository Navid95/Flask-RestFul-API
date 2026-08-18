from test import app


def test_routes(app):
    sorted_rules = sorted(app.url_map.iter_rules(), key=lambda r: r.rule)

    verbose = sorted(
        [(method, rule.endpoint, rule.rule)
         for rule in sorted_rules
         for method in sorted(rule.methods - {'HEAD', 'OPTIONS'})],
        key=lambda x: (x[2], x[0])
    )
    print(f"\n{'Method':<10} {'Endpoint':<55} Rule")
    print("-" * 100)
    for method, endpoint, rule in verbose:
        print(f"{method:<10} {endpoint:<55} {rule}")

    assert sorted_rules
