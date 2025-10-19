# Future Enhancement: Offline Neural TTS Models

**Status:** Planned for future implementation
**Priority:** Medium
**Complexity:** Medium
**Estimated Effort:** 4-8 hours

## Overview

Currently, the Sleep Soundscape Synthesizer uses **ElevenLabs API** for text-to-speech generation. While this provides excellent quality and authentic Romance language pronunciation, it has some limitations:

- **Cost**: ~$0.15-0.30 per 1,000 characters (~$0.15-0.30 per soundscape)
- **Online dependency**: Requires internet connection
- **Rate limits**: API quotas and request limits
- **Privacy**: Text sent to third-party service

This document outlines options for adding **offline neural TTS models** as an alternative backend, enabling:
- **Zero cost** after initial setup
- **Offline operation** (no internet required)
- **No rate limits** (generate unlimited soundscapes)
- **Privacy** (all processing happens locally)

---

## Recommended Offline TTS Options

### 1. Piper TTS (RECOMMENDED)

**GitHub:** https://github.com/rhasspy/piper

**Pros:**
- **Very fast** - Runs efficiently on CPU
- **Small models** - 10-50 MB per voice
- **Good quality** - Neural vocoder (VITS-based)
- **Multi-language** - Supports multiple Romance languages
- **Easy integration** - Simple Python API
- **Active development** - Well-maintained

**Cons:**
- **Quality** - Good but not as natural as ElevenLabs
- **Fewer voices** - Limited voice selection
- **Limited prosody control** - Less expressive than ElevenLabs

**Installation:**
```bash
pip install piper-tts
```

**Usage Example:**
```python
from piper import PiperVoice

# Load voice model (one-time download)
voice = PiperVoice.load('en_US-lessac-medium')

# Generate speech
text = "l�nhlhenreu y�olio�aullr�y m�od�yun"
audio = voice.synthesize(text)
```

**Available Romance Language Voices:**
- Spanish: `es_ES-*`
- French: `fr_FR-*`
- Portuguese: `pt_BR-*`
- Italian: `it_IT-*`

**Estimated Quality:** 7/10 (vs. ElevenLabs: 9.5/10)

---

### 2. Coqui TTS (Mozilla TTS)

**GitHub:** https://github.com/coqui-ai/TTS

**Pros:**
- **High quality** - Multiple neural architectures (Tacotron, VITS, etc.)
- **Voice cloning** - Can clone voices from samples
- **Multi-language** - Strong Romance language support
- **Fine-tuning** - Can train custom voices
- **SSML support** - Better prosody control

**Cons:**
- **Slower** - More computationally intensive
- **Larger models** - 100-500 MB per voice
- **Complex setup** - More dependencies
- **GPU recommended** - CPU generation is slow

**Installation:**
```bash
pip install TTS
```

**Usage Example:**
```python
from TTS.api import TTS

# Initialize with Spanish voice
tts = TTS(model_name="tts_models/es/css10/vits")

# Generate speech
tts.tts_to_file(
    text="se�or lheunaill ch�teau",
    file_path="output.wav"
)
```

**Estimated Quality:** 8/10 (vs. ElevenLabs: 9.5/10)

---

### 3. Tortoise TTS

**GitHub:** https://github.com/neonbjb/tortoise-tts

**Pros:**
- **Excellent quality** - Near ElevenLabs quality
- **Voice cloning** - Can clone any voice from 6+ seconds
- **Expressive** - Good prosody and emotion
- **Open source** - Fully customizable

**Cons:**
- **VERY slow** - 30+ seconds per sentence
- **GPU required** - Not practical for CPU-only systems
- **Large models** - 1-2 GB download
- **High memory usage** - Needs 8+ GB RAM

**Usage Example:**
```python
from tortoise import TextToSpeech
from tortoise.utils.audio import load_voice

tts = TextToSpeech()

# Generate speech (SLOW - ~30s per clip)
audio = tts.tts(
    text="l�nhlhenreu y�olio�aullr�y",
    voice_samples=None,  # Or custom voice
    preset='fast'  # Still slow!
)
```

**Estimated Quality:** 9/10 (vs. ElevenLabs: 9.5/10)

---

### 4. XTTS v2 (Coqui's Latest)

**GitHub:** Part of Coqui TTS

**Pros:**
- **Multilingual** - Single model for all languages
- **Voice cloning** - Excellent zero-shot cloning
- **Good quality** - Modern neural architecture
- **Emotion control** - Better expressiveness

**Cons:**
- **GPU recommended** - Slow on CPU
- **Large model** - ~2 GB download
- **Memory intensive** - Needs 6+ GB RAM

**Estimated Quality:** 8.5/10 (vs. ElevenLabs: 9.5/10)

---

## Comparison Matrix

| Feature | ElevenLabs | Piper | Coqui | Tortoise | XTTS v2 |
|---------|------------|-------|-------|----------|---------|
| **Quality** | 9.5/10 | 7/10 | 8/10 | 9/10 | 8.5/10 |
| **Speed** | Fast (API) | Very Fast | Moderate | Very Slow | Moderate |
| **Cost** | $0.15-0.30/k chars | Free | Free | Free | Free |
| **Offline** | L | | | | |
| **Setup Difficulty** | Easy | Easy | Moderate | Hard | Moderate |
| **Voice Variety** | 100+ voices | ~10/language | ~20/language | Custom | Custom |
| **Romance Languages** | Excellent | Good | Good | Good | Excellent |
| **SSML Support** | | L | Limited | L | L |
| **Prosody Control** | Excellent | Limited | Moderate | Good | Good |
| **GPU Required** | No | No | Recommended | Yes | Recommended |

---

## Implementation Plan

### Phase 1: Add Piper TTS Backend (4-6 hours)

**Goal:** Add Piper as a free offline alternative while keeping ElevenLabs as default.

**Changes Required:**

1. **Add dependency** (`requirements.txt`):
   ```txt
   piper-tts==1.2.0  # Optional, for offline TTS
   ```

2. **Create abstraction layer** (`src/audio/tts.py`):
   ```python
   def generate_speech(text, voice_id, output_path, config, backend='elevenlabs'):
       """
       Generate speech using specified backend.

       Args:
           backend: 'elevenlabs' (default) or 'piper'
       """
       if backend == 'piper':
           return _generate_with_piper(text, output_path, config)
       else:
           return _generate_with_elevenlabs(text, voice_id, output_path, config)

   def _generate_with_piper(text, output_path, config):
       """Generate speech using Piper TTS (offline, free)."""
       from piper import PiperVoice

       # Load voice from config
       voice_model = config.get('piper', {}).get('voice_model', 'es_ES-davefx-medium')
       voice = PiperVoice.load(voice_model)

       # Generate audio
       audio = voice.synthesize(text)

       # Save to file
       with open(output_path, 'wb') as f:
           f.write(audio)

       return True
   ```

3. **Update config** (`config/config.yaml`):
   ```yaml
   # TTS Backend Selection
   tts_backend: 'elevenlabs'  # or 'piper' for offline

   # Piper TTS Configuration (optional, for offline mode)
   piper:
     voice_model: 'es_ES-davefx-medium'  # Spanish voice
     # Other options: 'fr_FR-siwis-medium', 'pt_BR-faber-medium', 'it_IT-riccardo-x_low'
   ```

4. **Update CLI** (`src/pipeline/main.py`):
   ```python
   parser.add_argument(
       '--offline',
       action='store_true',
       help='Use offline TTS (Piper) instead of ElevenLabs API'
   )

   # In run_pipeline():
   backend = 'piper' if use_offline else 'elevenlabs'
   ```

5. **Update documentation**:
   - README.md: Note offline option
   - QUICKSTART.md: Add `--offline` flag example
   - CLAUDE.md: Document TTS backend configuration

**Testing:**
```bash
# Install Piper
pip install piper-tts

# Test offline mode
python -m src.pipeline.main --offline --clips 5
```

---

### Phase 2: Add Coqui TTS Backend (2-4 hours)

**Goal:** Add high-quality offline alternative with better prosody control.

Similar implementation to Piper, but with:
- Better quality
- Voice cloning capability
- More configuration options

---

### Phase 3: Voice Cloning Feature (6-8 hours)

**Goal:** Allow users to clone custom voices for personalized soundscapes.

**Implementation:**
```python
# Clone voice from samples
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Clone voice from audio samples
tts.tts_to_file(
    text="l�nhlhenreu y�olio�aullr�y",
    file_path="output.wav",
    speaker_wav="samples/my_voice.wav",  # Clone from this
    language="es"
)
```

**Use case:** Create soundscapes with your own voice or a friend's voice for personalization!

---

## Trade-offs for Users

### When to Use ElevenLabs (Current Default):
- You want **best quality** Romance language pronunciation
- You need **multiple distinct voices** (9 voices available)
- You want **SSML prosody control** (rate, pitch, emphasis)
- Cost is not a concern (~$0.15-0.30 per soundscape)
- You have internet connection

### When to Use Offline TTS (Future):
- You want **zero cost** (after initial setup)
- You need **offline operation** (no internet)
- You want **unlimited generation** (no rate limits)
- You value **privacy** (local processing)
- Quality is "good enough" for background ambience

---

## Cost Analysis

### Current (ElevenLabs Only):
- 20 clips � 50 characters average = 1,000 characters
- Cost per soundscape: **$0.15 - $0.30**
- 100 soundscapes: **$15 - $30**
- 1,000 soundscapes: **$150 - $300**

### With Offline TTS:
- Initial setup: **Free** (Piper) or **Free** (Coqui)
- Per soundscape: **$0.00**
- Unlimited soundscapes: **$0.00**
- **Break-even point:** ~50-100 soundscapes

**Recommendation:** Start with ElevenLabs, add offline option once you need >100 soundscapes or want offline capability.

---

## Technical Challenges

### 1. Romance Language Pronunciation
**Challenge:** Will Piper/Coqui pronounce our invented orthography correctly?

**Solution:**
- Test with Romance language models (es_ES, fr_FR, pt_BR)
- May need to tune phoneme selections for better pronunciation
- Could use multiple language models and blend them

### 2. Voice Consistency
**Challenge:** Each speaker personality should sound consistent.

**Solution:**
- Use single Piper voice per personality
- Or use Coqui voice cloning to create distinct voices
- Map personality traits to available voices

### 3. Prosody Control
**Challenge:** Offline models have limited SSML support.

**Solution:**
- Use Coqui's emotion/style controls
- Pre-process SSML to extract prosody hints
- Apply post-processing (tempo, pitch shifting via ffmpeg)

### 4. Performance
**Challenge:** CPU-based synthesis might be slow.

**Solution:**
- Use Piper (very fast, ~0.5s per clip on CPU)
- Cache commonly used phoneme combinations
- Consider GPU acceleration for Coqui/Tortoise

---

## Implementation Checklist

When implementing offline TTS:

- [ ] Add `piper-tts` to `requirements.txt` (optional dependency)
- [ ] Create TTS backend abstraction in `src/audio/tts.py`
- [ ] Add Piper backend implementation
- [ ] Update `config/config.yaml` with TTS backend selection
- [ ] Add `--offline` CLI flag to pipeline
- [ ] Update documentation (README, QUICKSTART, CLAUDE)
- [ ] Test with Romance language Piper models
- [ ] Verify pronunciation quality with accented characters
- [ ] Compare output quality vs. ElevenLabs
- [ ] Document quality/speed trade-offs
- [ ] (Optional) Add Coqui backend for higher quality
- [ ] (Optional) Add voice cloning feature

---

## Related Resources

**Piper TTS:**
- GitHub: https://github.com/rhasspy/piper
- Demo: https://rhasspy.github.io/piper-samples/
- Models: https://huggingface.co/rhasspy/piper-voices

**Coqui TTS:**
- GitHub: https://github.com/coqui-ai/TTS
- Documentation: https://tts.readthedocs.io/
- Models: https://huggingface.co/coqui

**Tortoise TTS:**
- GitHub: https://github.com/neonbjb/tortoise-tts
- Demo: https://nonint.com/2022/04/25/tortoise-dramatic-improvement-to-state-of-the-art-tts/

**General TTS Research:**
- VITS: https://arxiv.org/abs/2106.06103
- XTTS: https://arxiv.org/abs/2311.13490

---

## Conclusion

Adding offline neural TTS is a **worthwhile future enhancement** that would:
- Eliminate ongoing API costs
- Enable offline operation
- Remove rate limits
- Improve privacy

**Recommended approach:**
1. **Phase 1:** Add Piper TTS backend (easy, fast, good quality)
2. **Phase 2:** Add Coqui TTS backend (better quality, more features)
3. **Phase 3:** Add voice cloning for personalization

**Timeline:** Can be implemented incrementally over 10-20 hours total effort.

**Priority:** Medium - Current ElevenLabs implementation works well, but offline TTS would be a valuable alternative for cost-conscious or privacy-focused users.
