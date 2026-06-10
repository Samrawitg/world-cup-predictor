import sys

def check(label, fn):
    try:
        fn()
        print(f"  ✅  {label}")
        return True
    except Exception as e:
        print(f"  ❌  {label}  →  {e}")
        return False

print("\n🏆 World Cup Predictor — Environment Check\n")

results = [
    check("Python 3.9+",    lambda: (_ for _ in ()).throw(AssertionError(f"Need 3.9+")) if sys.version_info < (3,9) else None),
    check("flask",          lambda: __import__("flask")),
    check("pandas", lambda: __import__("pandas")),
    check("numpy", lambda: __import__("numpy")),
    check("scikit-learn", lambda: __import__("sklearn")),
    check("requests", lambda: __import__("requests")),
    check("beautifulsoup4", lambda: __import__("bs4")),
    check("matplotlib", lambda: __import__("matplotlib")),
    check("seaborn", lambda: __import__("seaborn")),
    check("sqlalchemy", lambda: __import__("sqlalchemy")),
    check("python-dotenv",  lambda: __import__("dotenv")),
    check("pytest", lambda: __import__("pytest")),
]

passed = sum(1 for r in results if r)
total  = len(results)
print(f"\n{'='*45}")
if passed == total:
    print(f"  🎉  All {total} checks passed! Ready for Day 2.")
else:
    print(f" ⚠️  {passed}/{total} passed — fix the ❌ items above.")
print(f"{'='*45}\n")
