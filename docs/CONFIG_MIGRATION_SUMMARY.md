# Config Migration Summary

All hardcoded parameters from ARCHITECTURE.md have been successfully migrated to `config/config.yaml`.

## Added Sections

### 1. ElevenLabs API Configuration
**Location:** Lines 7-14

```yaml
elevenlabs:
  api_url: "https://api.elevenlabs.io/v1/text-to-speech"
  voice_settings:
    stability: 0.5
    similarity_boost: 0.75
    style: 0.0
    use_speaker_boost: true
```

**Previously:** Hardcoded in `tts.py` lines 44, 175-177

---

### 2. Language Phonemes
**Location:** Lines 37-41

```yaml
language:
  phonemes:
    soft_consonants: ['l', 'm', 'n', 'r', 'v', 'j', 'w']
    medium_consonants: ['b', 'd', 'f', 's', 'z']
    hard_consonants: ['p', 't', 'k', 'g', 'ch', 'sh']
    vowels: ['a', 'e', 'i', 'o', 'u', 'ai', 'au', 'ea', 'ia', 'io']
```

**Previously:** Hardcoded in `generate_language.py` lines 24-29

---

### 3. Syllable Structure Probabilities
**Location:** Lines 44-47

```yaml
language:
  syllable_structure:
    onset_probability: 0.7       # 70% chance of initial consonant
    onset_first_syllable: 1.0    # First syllable always has onset
    coda_probability: 0.3        # 30% chance of final consonant
```

**Previously:** Hardcoded in `generate_language.py` lines 69, 76

---

### 4. Consonant Weighting
**Location:** Lines 51-54

```yaml
language:
  consonant_weighting:
    soft_ratio: 1.0      # Multiplier for soft consonants
    medium_ratio: 0.6    # Multiplier for medium consonants when softness=0
    hard_ratio: 0.4      # Multiplier for hard consonants when softness=0
```

**Previously:** Hardcoded in `generate_language.py` lines 36-38

---

### 5. Utterance Type Probabilities
**Location:** Lines 133-138

```yaml
utterance_type_probabilities:
  thinking: 0.05    # 5%
  agreement: 0.10   # 10% (cumulative 15%)
  laughter: 0.05    # 5% (cumulative 20%)
  question: 0.15    # 15% (cumulative 35%)
  normal: 0.65      # 65% (remaining)
```

**Previously:** Hardcoded in `generate_language.py` lines 164-177

**Note:** Must sum to 1.0

---

### 6. Micro Pause Probability
**Location:** Line 101

```yaml
breaks:
  micro_pause:
    probability: 0.2  # 20% chance between words
```

**Previously:** Hardcoded in `generate_ssml.py` line 88

---

## Benefits

1. **Full Configurability**: All "magic numbers" are now in config
2. **Easy Experimentation**: Change parameters without code changes
3. **Documentation**: Clear comments explain each parameter
4. **Customization**: Create different language flavors (harsh Germanic vs soft Romance)

## Next Steps (Phase 2)

Update the modules to actually READ these new config values:
- [ ] Update `src/generation/language.py` to use phonemes from config
- [ ] Update `src/generation/language.py` to use syllable_structure from config
- [ ] Update `src/generation/language.py` to use consonant_weighting from config
- [ ] Update `src/generation/language.py` to use utterance_type_probabilities from config
- [ ] Update `src/generation/ssml.py` to use micro_pause.probability from config
- [ ] Update `src/audio/tts.py` to use api_url from config
- [ ] Update `src/audio/tts.py` to use voice_settings from config

See ARCHITECTURE.md "Migration Path - Phase 1" for implementation details.
