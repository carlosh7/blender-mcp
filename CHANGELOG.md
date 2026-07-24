# Changelog

All notable changes to blender-mcp-ultra will be documented in this file.

## [1.0.0] - 2026-07-23

### Added
- **118 tools** across 16 categories
- **19 skills** for Claude Code/Cursor
- **Enterprise security**: AST validation, sandboxed execution, rate limiting
- **Performance**: LRU cache, tool result caching, lazy loading
- **MCP Adapter**: stdio to TCP bridge for opencode
- **Integration tests**: 16 tests with real Blender 5.2

### Security
- AST Validator with 200+ blocked patterns
- Sandboxed code execution with timeout protection
- Per-user rate limiting with token bucket algorithm
- Structured audit logging with file rotation
- Input validation for SQL injection, XSS, path traversal

### Performance
- LRU Cache with TTL support
- Tool result caching for repeated calls
- Lazy loading of tool categories
- Thread-safe cache operations

### Fixed
- `list()` builtin shadow in objects, materials, lights, modifiers
- Engine names: `BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE` for Blender 5.2
- Mesh cleanup: `to_mesh_clear()` instead of `bpy.data.meshes.remove()`
- Color conversion: `[c for c in color]` instead of `list(color)`
- `active_object`/`selected_objects` for background mode with `getattr()`
- AST validator: custom blocked names now work correctly
- Input validator: added `import os` pattern

### Compatible with
- Blender 4.0+
- Blender 5.2 LTS
- Python 3.10+
- opencode, Claude Desktop, Cursor

## [0.8.125] - 2026-07-18

### Added
- MCP Server with 6 core tools
- Blender socket server on port 9876
- Basic security validation

### Fixed
- Port conflicts
- Import issues

## [0.8.0] - 2026-07-01

### Added
- Initial release
- Basic MCP server
- Blender addon
