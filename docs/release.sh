#!/bin/bash -eux
# ./docs/release.sh [patch|minor|major|x.y.z]

[[ $(basename "$PWD") == docs ]] && cd ..


OLD=$(poetry version -s)

poetry version "$1"

NEW=$(poetry version -s)
DATE=$(date +%Y-%m-%d)

sed -ri "/__version__ /s/[0-9.]+/$NEW/" cmeel/__init__.py
sed -i "/^## \[Unreleased\]/a \\\n## [v$NEW] - $DATE" CHANGELOG.md
sed -i "/^\[Unreleased\]/s/$OLD/$NEW/" CHANGELOG.md
sed -i "/^\[Unreleased\]/a [v$NEW]: https://github.com/cmake-wheel/cmeel/compare/v$OLD...v$NEW" CHANGELOG.md

git add cmeel/__init__.py pyproject.toml CHANGELOG.md
git commit -m "Release v$NEW"
git tag -s "v$NEW" -m "Release v$NEW"
git push
git push --tags
