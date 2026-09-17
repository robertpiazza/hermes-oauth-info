# Hermes personal automation — OAuth information site

Public OAuth identity, privacy, and terms pages for Robert Piazza’s private, single-user Hermes automation.

When GitHub Pages and the custom domain are active, the site is available at:

- `https://hermes.robertpiazza.com/`
- `https://hermes.robertpiazza.com/privacy/`
- `https://hermes.robertpiazza.com/terms/`

## Scope

This repository contains only static public information required for OAuth branding. It has no analytics, cookies, JavaScript, or external page assets.

## Local validation

```bash
python3 validate.py
python3 -m unittest -q test_site.py
python3 -m http.server 8000 --bind 127.0.0.1
```

Then check the homepage, privacy page, and terms page at the local server origin.

`validate.py` is a lightweight structure/copy check; it is not legal advice.
