"""
Main Pipeline Orchestrator
Unified workflow for generating sleep soundscapes.

Usage:
    python -m src.pipeline.main
    python -m src.pipeline.main --clips 30
    python -m src.pipeline.main --skip-merge
    python -m src.pipeline.main --skip-spatial
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from src.utils.config_loader import load_config, ensure_output_dirs
from src.pipeline.clip_generator import generate_clips
from src.audio.merge import merge_clips
from src.audio.spatialize import create_spatial_soundscape


def run_pipeline(
    config_path: Optional[str] = None,
    num_clips: Optional[int] = None,
    skip_merge: bool = False,
    skip_spatial: bool = False,
    verbose: bool = True
) -> dict:
    """
    Run the complete sleep soundscape generation pipeline.

    Args:
        config_path: Path to config file (default: config/config.yaml)
        num_clips: Override number of clips to generate
        skip_merge: Skip merging step (only generate clips)
        skip_spatial: Skip spatialization step (only generate + merge)
        verbose: Print progress messages

    Returns:
        Dictionary with paths to generated files
    """
    if verbose:
        print("=" * 70)
        print("Sleep Soundscape Synthesizer - Unified Pipeline")
        print("=" * 70)

    # Stage 1: Load configuration
    if verbose:
        print("\n[1/4] Loading configuration...")

    config = load_config(config_path)
    ensure_output_dirs(config)

    # Override num_clips if specified
    if num_clips is not None:
        config['conversation']['num_clips'] = num_clips
        if verbose:
            print(f"  Overriding num_clips: {num_clips}")

    # Stage 2: Generate clips
    if verbose:
        print("\n[2/4] Generating audio clips...")

    clips_generated = generate_clips(config, verbose=verbose)

    if clips_generated == 0:
        print("\n[ERROR] No clips were generated. Aborting pipeline.")
        return {'success': False}

    # Stage 3: Merge clips (optional)
    merged_file = None
    if not skip_merge:
        if verbose:
            print("\n[3/4] Merging clips into sequential conversation...")

        try:
            merged_file = merge_clips(config, verbose=verbose)
            if verbose:
                print(f"  [OK] Created: {merged_file}")
        except Exception as e:
            print(f"  [ERROR] Merge failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
    else:
        if verbose:
            print("\n[3/4] Skipping merge step (--skip-merge)")

    # Stage 4: Create 3D soundscape (optional)
    spatial_file = None
    if not skip_spatial and not skip_merge:
        if verbose:
            print("\n[4/4] Creating 3D spatialized soundscape...")

        try:
            spatial_file = create_spatial_soundscape(config, verbose=verbose)
            if verbose:
                print(f"  [OK] Created: {spatial_file}")
        except Exception as e:
            print(f"  [ERROR] Spatialization failed: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
    elif skip_spatial:
        if verbose:
            print("\n[4/4] Skipping spatialization step (--skip-spatial)")
    elif skip_merge:
        if verbose:
            print("\n[4/4] Skipping spatialization step (requires merge)")

    # Summary
    if verbose:
        print("\n" + "=" * 70)
        print("Pipeline Complete!")
        print("=" * 70)
        print(f"\nGenerated files:")
        print(f"  Clips: {config['paths']['clips_dir']} ({clips_generated} files)")
        if merged_file:
            print(f"  Sequential: {merged_file}")
        if spatial_file:
            print(f"  3D Soundscape: {spatial_file} (RECOMMENDED)")
        print("\n" + "=" * 70)

    return {
        'success': True,
        'clips_dir': config['paths']['clips_dir'],
        'clips_generated': clips_generated,
        'merged_file': merged_file,
        'spatial_file': spatial_file
    }


def main():
    """Command-line interface for the pipeline."""
    parser = argparse.ArgumentParser(
        description='Sleep Soundscape Synthesizer - Generate soothing background chatter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.pipeline.main                    # Full pipeline with defaults
  python -m src.pipeline.main --clips 30         # Generate 30 clips
  python -m src.pipeline.main --skip-merge       # Only generate clips
  python -m src.pipeline.main --skip-spatial     # Generate + merge (no 3D)
  python -m src.pipeline.main --config custom.yaml  # Use custom config
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--clips',
        type=int,
        default=None,
        help='Number of clips to generate (overrides config)'
    )

    parser.add_argument(
        '--skip-merge',
        action='store_true',
        help='Skip merging clips into sequential conversation'
    )

    parser.add_argument(
        '--skip-spatial',
        action='store_true',
        help='Skip creating 3D spatialized soundscape'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    try:
        result = run_pipeline(
            config_path=args.config,
            num_clips=args.clips,
            skip_merge=args.skip_merge,
            skip_spatial=args.skip_spatial,
            verbose=not args.quiet
        )

        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)

    except FileNotFoundError as e:
        print(f"\n[ERROR] File not found: {e}")
        print("Make sure config/config.yaml exists.")
        sys.exit(1)

    except KeyError as e:
        print(f"\n[ERROR] Missing configuration key: {e}")
        print("Check that config/config.yaml has all required fields.")
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
