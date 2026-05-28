# Writing for the Ear

Scripts are read aloud. Written prose and spoken prose have different load-bearing rules. Most AI-generated scripts fail because they're structured as text, not speech.

## Key findings

### Pacing and rhythm are spoken phenomena

Much like music, speech has rhythm that's related to tempo and the alternation of stressed and unstressed syllables. Short, punchy sentences quicken the pulse and add energy; longer sentences slow the pace and allow reflection. A script made entirely of short declaratives reads as robotic; one made entirely of long sentences loses momentum. The fix is deliberate variation: if three short sentences appear consecutively, the fourth should be longer.

### Silence is part of the script

A single beat of silence after an important line adds power and resolve. Listeners need time to process verbal content and to watch what's on screen. Packing every second with words turns the script into an info drop.

### Write how people speak, not how they write

In most cases, people speak more informally than they write. Use contractions ("don't," "can't," "here's") — formal equivalents read stiff in a voice actor's mouth. Use words you naturally say. A line can be grammatically clean and still be hard to parse by ear on first listen. The test is reading aloud: if a clause trips you, rewrite it.

### AI-tell transitions to avoid

Models heavily overuse transitions like "Furthermore," "Moreover," "Additionally," and "In conclusion." They make prose feel stiff and formulaic. Use conversational connectives instead: "but," "and," "so," "then," "yet."

### Pacing anchors (for word-budget math)

| Engine / speaker | Approximate pace | Use this to compute word budget |
|---|---|---|
| Human voice actor / ElevenLabs | ~130–150 wpm | 90s voiced ≈ 200–225 words |
| AI TTS (general) | 150–170 wpm | 90s voiced ≈ 225–250 words |
| edge-tts Christopher at `+8%` rate (measured) | ~110 wpm | Slower because it inserts pauses; 90s voiced ≈ 165 words |

These anchors feed directly into the "plan ramp → compute word budget → then draft" workflow in `parallax-video` Stage 1.

### Retention costs come fast

Investing more in the first 7 seconds maximizes views and minimizes early drop-off. If viewers bounce in the first 5 seconds because the hook doesn't land, the algorithm deprioritizes the content downstream.

## Applied to Parallax

- The skill's `video-scriptwriting/SKILL.md` contains a "Writing for the Ear" section with these rules as bullets.
- The hard rule "maximum 2 em-dashes per piece" was removed after it produced over-clipped scripts. Em-dashes are fine when earned for emphasis, rhythm, or asides.
- Quality Check #2 in the skill is "Concise ≠ clipped" — explicitly to counteract the instinct to strip every line to a fragment.
- V1's hook ("Twenty minutes of research, in one sentence.") is deliberately 7 words — short is right for a hook, wrong for a hero paragraph.
- The trajectory paragraph at 2:00 is deliberately long (~55 words) — it's the narrative beat, needs room to breathe.

## Sources

- [How to Write a Voice-Over Script: 11 Tips From a VO Expert | Academy Voices](https://www.academyvoices.com/blog/how-to-write-a-voice-over-script)
- [Voiceover Script: How to Do It Right | WellSaid Labs](https://www.wellsaid.io/resources/blog/voiceover-script-how-to)
- [How to Write a Script for AI Voiceovers That Sounds Natural | Pixflow](https://pixflow.net/blog/how-to-write-a-script-for-ai-voiceovers-that-sounds-natural/)
- [15 Common Mistakes in AI Video Script Creation | HeyGen](https://www.heygen.com/blog/ai-to-write-script-for-video)
- [How to Make AI Voice Sound Less Robotic | Narration Box](https://narrationbox.com/blog/how-to-make-ai-voice-sound-less-robotic)
- [Video Script Writing: The Complete Guide for 2026 | Swarmify](https://swarmify.com/blog/script-writing/)
