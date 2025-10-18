#!/usr/bin/env python3
"""
Interactive Soundscape Controller
Adjust synthesizer parameters in real-time
"""

import os
import sys
import threading
from soundscape_synthesizer import SoundscapeSynthesizer


class InteractiveSynthesizer:
    """Wrapper for synthesizer with interactive controls"""
    
    def __init__(self, api_key: str):
        self.synth = SoundscapeSynthesizer(api_key)
        self.running = False
        self.generation_thread = None
    
    def start_generation(self, save_files: bool = False):
        """Start generating soundscape in background thread"""
        if self.running:
            print("Already running!")
            return
        
        self.running = True
        self.generation_thread = threading.Thread(
            target=self._generation_loop,
            args=(save_files,),
            daemon=True
        )
        self.generation_thread.start()
        print("🎵 Soundscape generation started!")
    
    def stop_generation(self):
        """Stop generating soundscape"""
        self.running = False
        if self.generation_thread:
            self.generation_thread.join(timeout=2)
        print("⏹  Soundscape generation stopped!")
    
    def _generation_loop(self, save_files: bool):
        """Background loop that generates audio continuously"""
        utterance_count = 0
        while self.running:
            try:
                audio_data, pause_duration = self.synth.generate_utterance_audio()
                utterance_count += 1
                
                if save_files:
                    filename = f"soundscape_{utterance_count:04d}.mp3"
                    self.synth.save_audio(audio_data, filename)
                
                # Sleep for pause duration (checking running flag periodically)
                elapsed = 0
                sleep_interval = 0.1
                while elapsed < pause_duration and self.running:
                    import time
                    time.sleep(sleep_interval)
                    elapsed += sleep_interval
                    
            except Exception as e:
                print(f"Error in generation: {e}")
                import time
                time.sleep(1)
    
    def show_parameters(self):
        """Display current parameter values"""
        print("\n📊 Current Parameters:")
        print("─" * 50)
        for param, value in self.synth.params.items():
            print(f"  {param:25s}: {value:.2f}")
        print("─" * 50)
    
    def show_help(self):
        """Show available commands"""
        print("\n📖 Available Commands:")
        print("─" * 50)
        print("  start              - Start soundscape generation")
        print("  stop               - Stop soundscape generation")
        print("  params / p         - Show current parameters")
        print("  set <param> <val>  - Set parameter value")
        print("  preset <name>      - Load a preset")
        print("  help / h           - Show this help")
        print("  quit / q           - Exit program")
        print("\n  Parameters you can set:")
        print("    speech_rate          (0.5 - 1.2)")
        print("    conversation_density (0.1 - 1.0)")
        print("    pitch_variation      (0.0 - 1.0)")
        print("    softness             (0.0 - 1.0)")
        print("    laughter_frequency   (0.0 - 0.5)")
        print("    num_speakers         (2 - 5)")
        print("\n  Example: set softness 0.95")
        print("─" * 50)
    
    def load_preset(self, preset_name: str):
        """Load a parameter preset"""
        presets = {
            'gentle': {
                'speech_rate': 0.75,
                'conversation_density': 0.4,
                'pitch_variation': 0.3,
                'softness': 0.9,
                'laughter_frequency': 0.1,
                'num_speakers': 2,
            },
            'meditative': {
                'speech_rate': 0.6,
                'conversation_density': 0.2,
                'pitch_variation': 0.2,
                'softness': 0.95,
                'laughter_frequency': 0.05,
                'num_speakers': 2,
            },
            'lively': {
                'speech_rate': 1.0,
                'conversation_density': 0.8,
                'pitch_variation': 0.6,
                'softness': 0.6,
                'laughter_frequency': 0.3,
                'num_speakers': 4,
            },
            'intimate': {
                'speech_rate': 0.8,
                'conversation_density': 0.5,
                'pitch_variation': 0.4,
                'softness': 0.85,
                'laughter_frequency': 0.2,
                'num_speakers': 2,
            },
            'cafe': {
                'speech_rate': 0.9,
                'conversation_density': 0.7,
                'pitch_variation': 0.5,
                'softness': 0.7,
                'laughter_frequency': 0.25,
                'num_speakers': 3,
            },
        }
        
        if preset_name not in presets:
            print(f"❌ Unknown preset: {preset_name}")
            print(f"   Available presets: {', '.join(presets.keys())}")
            return
        
        preset = presets[preset_name]
        for param, value in preset.items():
            self.synth.set_parameter(param, value)
        
        print(f"✅ Loaded preset: {preset_name}")
        self.show_parameters()
    
    def set_parameter(self, param_name: str, value_str: str):
        """Set a parameter value"""
        try:
            value = float(value_str)
            self.synth.set_parameter(param_name, value)
            print(f"✅ Set {param_name} = {value}")
        except ValueError as e:
            print(f"❌ Invalid value: {value_str}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_interactive(self):
        """Run the interactive command loop"""
        print("=" * 50)
        print("  🌙 Sleep Soundscape Synthesizer")
        print("  Interactive Controller")
        print("=" * 50)
        self.show_help()
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                
                if cmd in ['quit', 'q', 'exit']:
                    self.stop_generation()
                    print("Goodbye! 👋")
                    break
                
                elif cmd == 'start':
                    save_files = '--save' in parts or '-s' in parts
                    self.start_generation(save_files=save_files)
                
                elif cmd == 'stop':
                    self.stop_generation()
                
                elif cmd in ['params', 'p']:
                    self.show_parameters()
                
                elif cmd in ['help', 'h']:
                    self.show_help()
                
                elif cmd == 'set':
                    if len(parts) != 3:
                        print("Usage: set <parameter> <value>")
                    else:
                        self.set_parameter(parts[1], parts[2])
                
                elif cmd == 'preset':
                    if len(parts) != 2:
                        print("Usage: preset <name>")
                        print("Available: gentle, meditative, lively, intimate, cafe")
                    else:
                        self.load_preset(parts[1])
                
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point"""
    # Get API key
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("Please set ELEVENLABS_API_KEY environment variable")
        print("Or enter it now:")
        api_key = input("API Key: ").strip()
        if not api_key:
            print("No API key provided. Exiting.")
            return
    
    # Create and run interactive synthesizer
    controller = InteractiveSynthesizer(api_key)
    controller.run_interactive()


if __name__ == "__main__":
    main()
