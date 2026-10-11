# VIDYA / Education Extension — Language, Dictionaries, Kids' Grammar & Miniature 3D Learning Family

**Version:** 1.0  
**Date:** 2026-10-11  
**Parent:** `EDU` → `VIDYA / विद्या — Education & World Wisdom`  
**Change type:** additive sub-agent/content capability specification; does not create a new top-level agent or renumber existing EDU slots.  
**Status:** proposed repository configuration pending CI and owner review; this document does not claim the content pipeline is deployed or live.

## 1. Purpose

Extend VIDYA with a multilingual language-learning fabric for children and lifelong learners: vocabulary, dictionaries, pronunciation, spelling, reading, writing, grammar, translation, language comparison and culturally grounded stories. Use a recurring miniature 3D cartoon family as an optional visual teaching cast, including the owner-requested scene: **an AI miniature 3D cartoon family standing on a giant kitchen table, toy-sized proportions, ultra-cute expressive faces, vibrant colours, cinematic lighting, highly detailed animated-movie style**.

The kitchen-table scene is a visual setting, not a requirement that every lesson be about food. Use it as a playful scale-world where the family can explore words, objects, letters, sounds, stories and everyday life. Keep characters original and avoid copying recognizable studio characters, protected designs, voices or signature scenes.

## 2. Placement and identity

- Parent knowledge fabric: `EDU` / `VIDYA`.
- Suggested capability group: `VIDYA-BHASHA` (भाषा — language).
- Suggested stable topic IDs below are child capabilities under Education, not new root agents.
- Preserve all existing `EDU-S*` identities and legacy mappings. Do not overwrite the historical V16.7.24 snapshot or change counts without reconciliation.
- Route children's stories and educational cartoons through Education. Bhakti content remains respectful and source-aware under its existing owner; cross-category reuse must retain the original owner and provenance.

## 3. Language and dictionary capabilities

### 3.1 Vocabulary and lexical learning
- Word of the day/week; age- and level-banded vocabulary; themes (home, family, kitchen, school, nature, science, emotions, safety, travel, arts, sport, community and careers).
- Meaning, synonyms, antonyms, homophones, homonyms, roots, prefixes/suffixes, word families, compounds, idioms, phrases, proverbs and contextual usage.
- Word origins and historical evolution when reliable evidence is available; distinguish established etymology from folk explanation.
- Spelling, syllables, phonemes, transliteration, pronunciation guides, minimal pairs and listening/repeat activities.
- Picture dictionaries, tactile/object-based prompts, flashcards, matching games, quizzes, spaced-repetition packs and printable classroom sheets.

### 3.2 Dictionary families
- Monolingual dictionaries, bilingual dictionaries, multilingual dictionaries, learner dictionaries, children's picture dictionaries, subject/technical glossaries, idiom/proverb dictionaries, etymological dictionaries and historical dictionaries.
- Word entries should support: headword; language and script; pronunciation/audio reference; part of speech; child-safe definitions; example sentences; inflections; grammatical gender/class where relevant; synonyms/antonyms; register/dialect labels; transliteration; translation equivalents; source and licence/provenance; confidence; review date.
- Never invent a dictionary citation or imply that generated translations are authoritative. Flag regional, dialectal, contested or low-confidence meanings for review.

### 3.3 Grammar and literacy
- Alphabet/varnamala, scripts, letter formation, vowels/consonants, matras/diacritics, phonics, phonemic awareness, reading fluency, comprehension, handwriting, spelling, punctuation and composition.
- Parts of speech; nouns/pronouns; gender/number/case; verbs and tense/aspect/mood; agreement; adjectives/adverbs; postpositions/prepositions; sentence structure; word order; clauses; direct/indirect speech; active/passive voice; conjunctions; questions/negation; honorifics/register; sandhi/samasa and language-specific grammar where applicable.
- Teach grammar descriptively and respectfully; do not mark a legitimate dialect or home-language variety as inherently inferior.
- Age bands: preschool; early primary; upper primary; middle school; secondary; exam/advanced; adult and professional learner. Adapt complexity, examples and assessment to the selected band.

## 4. Language coverage

### Global and international
Support an extensible language registry, not a hard-coded finite list. Prioritize English, major world languages requested by users, and languages supported by reviewed data, fonts, speech and quality evaluation. Candidate packs may include Spanish, French, Portuguese, German, Italian, Arabic, Mandarin Chinese, Japanese, Korean, Russian and other languages as evidence, capability and demand permit.

### Indian languages
- Sanskrit — Devanagari and relevant transliteration systems; classical grammar and source-aware textual study.
- Hindi and English — foundational literacy, advanced grammar, bilingual dictionaries and translation.
- All 22 languages in the Eighth Schedule of the Constitution of India: Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri, Konkani, Maithili, Malayalam, Manipuri (Meitei), Marathi, Nepali, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu and Urdu.
- Extend to additional Indian regional, tribal, community and local languages/dialects when language identifiers, community preferences, rights-cleared sources and suitable reviewers are available. Examples may include Tulu, Bhojpuri, Rajasthani varieties, Chhattisgarhi, Haryanvi, Khasi, Garo, Mizo, Kokborok and others; do not misrepresent this examples list as exhaustive or as constitutional-schedule status.
- Respect scripts, transliteration preferences, dialect variation, names, cultural context and community review. Support code-switching and Hinglish only when explicitly selected or pedagogically appropriate.

### Cross-language functions
- Source/target language selection; side-by-side text; transliteration separate from translation; sentence-level alignment; word-by-word gloss; pronunciation comparison; grammar contrast; false friends; cognates; loanwords; translation memory; glossary export.
- Keep original script and normalized forms where appropriate. Do not silently erase diacritics or alter proper names.

## 5. Suggested child capability IDs

| Capability ID | Display name | Scope |
|---|---|---|
| `EDU-BHASHA-VOCAB` | शब्द-भंडार / Vocabulary Studio | Vocabulary, word families, idioms and spaced repetition |
| `EDU-BHASHA-DICT` | शब्दकोश / Dictionary Fabric | Learner, picture, bilingual, multilingual and specialist dictionaries |
| `EDU-BHASHA-GRAMMAR` | व्याकरण / Grammar for Every Age | Child-first grammar, writing and language-specific rules |
| `EDU-BHASHA-SANSKRIT` | संस्कृत विद्या / Sanskrit Learning | Sanskrit vocabulary, grammar, pronunciation and source-aware reading |
| `EDU-BHASHA-HINDI` | हिंदी भाषा / Hindi Learning | Hindi literacy, grammar, vocabulary and usage |
| `EDU-BHASHA-ENGLISH` | English Language Studio | English literacy, vocabulary, grammar and pronunciation |
| `EDU-BHASHA-INDIC` | भारतीय भाषा सेतु / Indian Languages Bridge | Scheduled and additional Indian languages, scripts and regional variants |
| `EDU-BHASHA-GLOBAL` | विश्व भाषा सेतु / Global Language Bridge | Extensible world-language learning and translation |
| `EDU-BHASHA-SPEECH` | श्रवण-वाचन / Listen, Speak & Read | Audio, pronunciation, speech practice and accessibility |
| `EDU-STORY-3D-FAMILY` | नन्हा ज्ञान-परिवार / Miniature Learning Family | Original toy-scale 3D characters teaching language and school topics |
| `EDU-STORY-VISUAL` | चित्र-कथा प्रयोगशाला / Visual Story Lab | Picture books, comics, animation, stop-motion-inspired visuals and short video |
| `EDU-TREND-INTEL` | पाठ्य-रुझान / Learning Trend Intelligence | Trend discovery, evidence checks and age-appropriate curriculum opportunities |

These are proposed stable IDs for new child capabilities. Before activation, reconcile them against the live registry to prevent duplicate IDs.

## 6. Miniature 3D cartoon family — art and story bible

### Core visual brief
“An original AI miniature 3D cartoon family standing on a giant kitchen table, toy-sized proportions, ultra-cute expressive faces, vibrant colours, cinematic lighting, highly detailed animated-movie style.” Add carefully staged miniature-scale props: a giant alphabet card, oversized spoon, fruit, notebooks, crayons, building blocks, dictionary pages and labelled objects. Keep the family clearly toy-sized by showing tabletop grain and familiar oversized household objects.

### Art direction
- Warm, welcoming, polished 3D character animation; soft tactile materials; expressive but readable faces; vibrant yet harmonious palette; cinematic key/fill/rim lighting; shallow depth of field used only when it does not hide learning content.
- Original family members with distinct silhouettes, clothing, ages and personalities. No unlicensed character likenesses, brand logos or copied studio-specific designs.
- Stable character sheets: front/side/back views, expressions, scale reference, costume palette, accessibility notes and model/version IDs. Costume changes can be seasonal or weekly while preserving recognizable identity.
- Visual continuity across episodes; locked character, prop, setting and colour references; subtitle-safe composition; no text baked into generated images unless spelling can be verified.
- The kitchen-table setting may recur, but episodes can move to a classroom, garden, library, market, museum, village, city, space model or imaginary letter-world as appropriate.

### Learning episode pattern
1. Friendly hook and one clear learning goal.
2. Introduce 3–8 new words (age/level dependent), with correct script, meaning and audio.
3. Show words through an object, action, story or comparison.
4. Let a character make a harmless, relatable mistake; model the correction kindly.
5. Invite the child to speak, point, match, read, write or choose.
6. Recap, retrieval quiz and optional parent/teacher prompt.
7. End card with level, languages, learning outcomes, source notes and accessibility options.

### Formats
Picture dictionary; vocabulary song/rhyme with original lyrics and licensed/original music; animated grammar mini-lesson; 15–60 second short; 2–6 minute episode; longer story; interactive quiz; printable worksheet; audiobook; read-along; comic strip; flashcard deck; classroom presentation; downloadable lesson pack; subtitles/dubbing/localized versions; live/interactive lesson only with adult controls.

## 7. Education content taxonomy — reusable across subjects

Every lesson/product may be tagged with one or more of:
- Foundations: alphabet, sounds, words, numbers, observation, reading and writing.
- Language & literature: vocabulary, dictionaries, grammar, poetry, stories, drama, translation and comparative literature.
- Mathematics and logic; natural sciences; environment and Earth; space and astronomy; computing, AI literacy and digital safety; engineering and design.
- Social studies, geography, civics, history, cultures, heritage and current affairs.
- Arts, music, craft, movement, sports, life skills, health/safety and financial literacy.
- Indian knowledge systems, philosophy, classical texts and traditions with provenance and distinction between tradition, interpretation and independently evidenced history.
- Study skills, research, exams, projects, professional learning, career exploration and lifelong learning.

Universal knowledge lifecycle: **Origin → Oldest known evidence / early forms → Historical evolution → Regional and global context → Present use → Current trends → Future possibilities**. Do not invent an “oldest” claim when the evidence is uncertain.

## 8. Visual, narrative and learning styles

Allow user/teacher choice and per-lesson adaptation:
- Visual: miniature 3D animation, stylized 2D, watercolor, paper cut-out, clay/toy look, storybook illustration, comic, infographic, diagrams, motion graphics, live-action classroom demo and mixed media.
- Narrative: gentle teacher, curious family adventure, call-and-response, mystery/puzzle, quest, comedy, fable, role-play, documentary explainer, song/rhyme and project-based learning.
- Delivery: text, image sequence, captioned video, audio, dubbing, sign-supported/accessible presentation where supported, interactive practice, printable and offline pack.
- Accessibility: captions/transcripts, readable type, contrast checks, dyslexia-aware layout options, audio speed controls, reduced motion, alt text and keyboard/touch-friendly activities.

A style preset changes presentation, not facts, identity, safety rules or rights requirements. Do not imitate a living artist's style or clone a recognizable performer; use high-level visual attributes and original voices.

## 9. Trend intelligence and curriculum freshness

- Discover trends from permitted public sources and platform analytics where authorized; track date, region, audience, language, query/topic, source URL, evidence strength and confidence.
- Separate **observed trend**, **search demand**, **curriculum importance**, **educational quality** and **commercial opportunity**; a high-view trend is not automatically a good lesson.
- Evaluate usefulness, factual reliability, age suitability, cultural sensitivity, accessibility, rights, production effort and measurable learning outcome before prioritizing.
- Refresh trend signals on a configurable schedule; mark stale signals and show last-checked timestamps. Use trend tools as discovery inputs, not as unquestioned truth.
- Create original adaptations rather than copying viral videos, scripts, music, characters, thumbnails or creator identities.
- No engagement bait, fear, shame, manipulative streaks, unsafe challenges or child-directed pressure to purchase. Do not profile children for targeted advertising.

## 10. Quality, safety, privacy and rights gates

Before content is released:
1. Verify facts, dictionary definitions, translations, grammar rules and examples with reliable references and qualified language review where feasible.
2. Record source, licence, attribution requirements, generated asset provenance and permitted use for text, images, fonts, audio, music and voice.
3. Human-review cultural nuance, regional-language accuracy, age suitability, pronunciation and claims of historical origin.
4. Check generated text embedded in images; prefer compositing verified typography in post-production.
5. Apply child privacy by default: collect minimal data, avoid public disclosure of a child's identity/location/school, obtain required guardian consent for any personal data or voice recording, and provide deletion/retention controls.
6. No unmoderated child-to-agent private messaging, external links or public comments; provide adult/teacher controls and report/escalation paths.
7. Label synthetic media when appropriate; never present a fabricated source, expert endorsement or real-person likeness as authentic.
8. Obtain owner approval before public publishing, monetized distribution, paid promotion or external account actions.

## 11. Product, distribution and Kuber measurement

Potential products: free discovery lessons; vocabulary packs; printable worksheets; multilingual dictionary packs; parent/teacher resources; school licensing; curriculum-aligned series; audiobooks; books; courses; subscriptions where legally and ethically appropriate; sponsorships subject to child-safety rules; translation/localization services and licensing of original characters/assets.

Track per asset: content ID; EDU child capability ID; language/script; age band; source/provenance; rights status; human review; creation/editing cost; publication approval; platform and publication ID; views/retention where available; learning completion/assessment results; revenue/receivable/payment; refunds; attribution; Kuber reconciliation and audit status. Do not promise revenue. Child-directed content must not use inappropriate targeted advertising or exploitative monetization.

## 12. Definition of done

- [ ] Capability IDs checked against the current registry; no collisions.
- [ ] Existing EDU slots and historical snapshots preserved.
- [ ] Language/script list and scope reviewed by a qualified reviewer.
- [ ] At least one sample vocabulary entry, dictionary entry, grammar lesson and cartoon storyboard pass content QA.
- [ ] All generated visuals/voices/music have documented rights and provenance.
- [ ] Child safety, accessibility, captions and guardian/teacher controls reviewed.
- [ ] Trend records have source, date, confidence and human prioritization.
- [ ] Build/validation tests pass; actual integrations are separately verified.
- [ ] Publishing remains approval-gated; revenue is recorded only from actual platform/account evidence.

**Implementation note:** This is an additive specification for VIDYA. It does not claim agents, dictionaries, models, trend feeds, media pipelines, platform accounts or revenue are already connected or live.
