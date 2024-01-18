# Version 1.3.4 (unreleased)

## 💫 Improvements

- Update SQLAlchemy 1.3 to 1.4
- Compatible with GeoNature 2.14 (develop)

## 🐛 Bug Fixes

- list in prefilters must now be separeted by a pipe ("|") instead of a comma (";"). This change is due to the new version of Flask (3.0.x) which split
  parameters using both commas and ampersand ("&")
