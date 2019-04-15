# uplyfile.py

Uplyfile plugin for python http framworks.

# Storage
To configure storage one has to provide (in the settings file) API keys via `PUBLIC_KEY` and `SECRET_KEY` in the `UPLYFILE_STORAGE` namespace:
`settings.py`
```python
UPLYFILE_STORAGE = {
  "PUBLIC_KEY": "your_public_key",
  "SECRET_KEY": "your_secret_key"
}
```

List of recognizable keys:
- `API_VERSION`   - API version of Uplyfile which is specified in URLs, defaults to `"v1"`
- `BASE_API_URL`  - self-descriptive, defaults to `"https://uplycdn.com/api/"`
- `MAPPINGS_FILE` - path to file where all name <-> URL mappings will be saved, defaults to `"mappings.json"`
