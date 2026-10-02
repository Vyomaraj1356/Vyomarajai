# DR sync verification trigger

This file exists solely to trigger an authenticated Primary → DR verification run after the latest DR workflow repair.

The authoritative result is the GitHub Actions run for this commit, including PRIMARY_TREE_SHA, DR_VERIFIED_TREE_SHA, DATA_MATCH and READ_AFTER_WRITE_SHA.
