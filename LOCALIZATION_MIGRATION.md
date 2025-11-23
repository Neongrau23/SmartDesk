# Localization Migration Guide

## Overview

The localization system has been refactored from a flat dictionary structure to a nested, hierarchical structure. This improves organization, readability, and maintainability.

## Changes

### Old Structure (Flat)
```python
TEXT = {
    "DH_ERROR_PATH_INVALID": "✗ Fehler: Pfad '{path}' ist ungültig...",
    "DH_ERROR_NAME_EXISTS": "✗ Fehler: Desktop '{name}' existiert bereits.",
    "IM_ERROR_SHELLDLL_NOT_FOUND": "[IconManager ERROR] SHELLDLL_DefView-Fenster nicht gefunden.",
    # ... 100+ entries
}

# Usage
print(get_text("DH_ERROR_PATH_INVALID", path="/foo"))
```

### New Structure (Nested)
```python
TEXT = {
    "desktop_handler": {
        "error": {
            "path_invalid": "✗ Fehler: Pfad '{path}' ist ungültig...",
            "name_exists": "✗ Fehler: Desktop '{name}' existiert bereits."
        }
    },
    "icon_manager": {
        "error": {
            "shelldll_not_found": "[IconManager ERROR] SHELLDLL_DefView-Fenster nicht gefunden."
        }
    }
}

# Usage with dot notation
print(get_text("desktop_handler.error.path_invalid", path="/foo"))
```

## Key Categories

The new structure organizes keys into the following categories:

### 1. `logo`
- `logo.ascii` - ASCII art logo

### 2. `ui`
- `ui.menu.main.*` - Main menu items
- `ui.menu.settings.*` - Settings menu items
- `ui.prompts.*` - User input prompts
- `ui.status.*` - Status indicators
- `ui.headings.*` - Section headings
- `ui.messages.*` - User-facing messages
- `ui.errors.*` - UI error messages

### 3. `desktop_handler`
- `desktop_handler.error.*` - Error messages
- `desktop_handler.success.*` - Success messages
- `desktop_handler.info.*` - Informational messages
- `desktop_handler.warn.*` - Warning messages
- `desktop_handler.prompts.*` - User prompts

### 4. `icon_manager`
- `icon_manager.error.*` - Error messages
- `icon_manager.info.*` - Informational messages
- `icon_manager.warn.*` - Warning messages
- `icon_manager.debug.*` - Debug messages

### 5. `system`
- `system.info.*` - System-related messages

### 6. `main`
- `main.error.*` - Main module errors
- `main.warn.*` - Main module warnings
- `main.info.*` - Main module info
- `main.success.*` - Main module success messages
- `main.usage.*` - Usage instructions

### 7. `storage`
- `storage.error.*` - Storage/file operation errors

### 8. `path_validator`
- `path_validator.error.*` - Path validation errors

### 9. `registry`
- `registry.error.*` - Registry operation errors

## Migration Examples

### Desktop Handler
```python
# Old
get_text("DH_ERROR_PATH_INVALID", path=desktop_path)
get_text("DH_SUCCESS_CREATE", name=desktop_name)

# New
get_text("desktop_handler.error.path_invalid", path=desktop_path)
get_text("desktop_handler.success.create", name=desktop_name)
```

### UI Messages
```python
# Old
get_text("PROMPT_CHOOSE")
get_text("STATUS_ACTIVE")

# New
get_text("ui.prompts.choose")
get_text("ui.status.active")
```

### Icon Manager
```python
# Old
get_text("IM_ERROR_SHELLDLL_NOT_FOUND")
get_text("IM_INFO_READING_ICONS")

# New
get_text("icon_manager.error.shelldll_not_found")
get_text("icon_manager.info.reading")
```

## Benefits

✅ **Better Organization**: Logical grouping by context  
✅ **Shorter Keys**: No redundant prefixes  
✅ **Maintainability**: Easier to navigate and extend  
✅ **i18n Ready**: Prepared for adding more languages  
✅ **IDE Support**: Better autocomplete and navigation  

## Updated get_text() Function

The `get_text()` function now supports dot notation:

```python
def get_text(key: str, **kwargs) -> str:
    """
    Retrieves a localized text using dot notation.
    
    Args:
        key: Dot-separated path to the text (e.g., "ui.menu.main.switch")
        **kwargs: Format parameters for the text template
        
    Returns:
        Formatted text string, or error message if key not found
        
    Examples:
        get_text("ui.menu.main.switch")
        get_text("desktop_handler.error.path_invalid", path="/foo")
    """
```

## Error Handling

If a key is not found, `get_text()` returns:
```
<key.path nicht gefunden>
```

This makes missing keys easy to identify during development.
