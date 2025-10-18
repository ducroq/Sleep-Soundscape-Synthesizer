# Archive Directory

This directory contains legacy scripts from before Phase 1 modularization.

**Status:** Frozen for historical reference
**Use:** For backward compatibility only
**Recommendation:** Use new src/ modules instead

## Legacy Scripts

These scripts still work but are no longer actively maintained:

- `generate_soundscape.py` - Original main orchestrator
- `merge_audio.py` - Sequential conversation merger
- `spatialize_audio.py` - 3D soundscape creator

## Migration Path

For new development, use the modular structure in `src/`:

```bash
# Old way (archive)
cd archive
python generate_soundscape.py

# New way (Phase 2 - coming soon)
python -m src.pipeline.main
```

See main [README.md](../README.md) for current usage instructions.
