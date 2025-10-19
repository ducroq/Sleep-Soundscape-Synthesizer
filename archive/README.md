# Archive Directory

This directory contains legacy scripts from before the Phase 1 & 2 refactoring.

**Status:** Frozen for backward compatibility
**Use:** Historical reference and backward compatibility only
**Recommendation:** Use unified pipeline instead: `python -m src.pipeline.main`

## Legacy Scripts

These scripts still work but are no longer actively maintained:

- `generate_soundscape.py` - Original main orchestrator
- `merge_audio.py` - Sequential conversation merger
- `spatialize_audio.py` - 3D soundscape creator

## Migration Guide

The archive scripts require running 3 commands manually. The new unified pipeline does everything in one command:

```bash
# Old way (3 manual steps)
cd archive
python generate_soundscape.py  # Step 1: Generate clips
python merge_audio.py          # Step 2: Merge clips
python spatialize_audio.py     # Step 3: Create 3D soundscape
cd ..

# New way (✅ Phase 2 Complete)
python -m src.pipeline.main    # One command does everything!
```

### CLI Options

The unified pipeline supports flexible options:

```bash
python -m src.pipeline.main --clips 30       # Custom clip count
python -m src.pipeline.main --skip-merge     # Only generate clips
python -m src.pipeline.main --skip-spatial   # Skip 3D spatialization
python -m src.pipeline.main --help           # See all options
```

See main [README.md](../README.md) for current usage instructions.
