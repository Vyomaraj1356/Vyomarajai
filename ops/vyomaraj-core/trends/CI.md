# Trend-intake CI integration note

The intake utility and its tests are standard-library Python. Run the following in repository CI after adding the directory to the offline test suite:

```sh
python3 -m unittest discover -s ops/vyomaraj-core/trends -p 'test_*.py' -v
```

The test suite uses temporary local files only. It makes no network calls, reads no credentials, and cannot publish. Do not run `--write` against production queues from CI.
