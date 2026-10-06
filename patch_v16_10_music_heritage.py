#!/usr/bin/env python3
"""Add the Sufi, ghazal and studio-show format layer to the music lane (V16.10).

Owner request, 2026-10-06: "under music, research/update/modify/integrate/inherit all contents
of new and old of Sufi, Ghazal, Coke Studio and its similar shows."

How this patch answers it honestly:
  * Heritage and format records are ADDED to the existing pack (39 -> 63 starter cards). They
    are context, credits and programme structure only. No episode, recording, lyric, artwork or
    brand asset is imported, and every card says so in its own words.
  * Shows are recorded as FORMATS with their public history (who produced them, when they began,
    what the format is), because the format is what we may inherit; the content is not ours.
  * Four original programme formats are added with licence_status
    'owned_original_not_yet_recorded' and a rights_basis line. They claim no credits yet and
    carry no media. This is the inheritance route: our own mehfil, kafi, ghazal and Navaratri
    cycles, built on the structures above, with our own names, scripts and credits.
  * The pinned registry and the 32-file historical catalog are not touched. No new agents are
    created: everything binds to the six existing ENT-MUS-S1-S6 slots, canonical names UNKNOWN.

Run:  python3 patch_v16_10_music_heritage.py          (writes content.json)
      python3 patch_v16_10_music_heritage.py --check   (verifies the pack without writing)
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACK = ROOT / 'ops/vyomaraj-core/music-experience/content.json'
EXTENSIONS = ROOT / 'ops/vyomaraj-core/experience/CONTENT_EXTENSIONS.json'
UPDATED = '2026-10-06'
CONTEXT_ONLY = ('Format context only: no episode, recording, lyric, artwork or brand asset is '
                'imported, copied or rehosted.')
ORIGINAL = 'owned_original_not_yet_recorded'

SOURCES = [
    ('cs-pak', 'Wikipedia — Coke Studio Pakistan',
     'https://en.wikipedia.org/wiki/Coke_Studio_Pakistan',
     'Season list, house-band format and producer runs as described at the check date.'),
    ('cs-franchise', 'Wikipedia — Coke Studio (international franchise)',
     'https://en.wikipedia.org/wiki/Coke_Studio',
     'Franchise origin and the editions outside Pakistan.'),
    ('cs-bangla', 'Wikipedia — Coke Studio Bangla',
     'https://en.wikipedia.org/wiki/Coke_Studio_Bangla',
     'Bengali-language edition and its 2022 launch.'),
    ('cs-dewarists-et', 'The Economic Times — Coke Studio and The Dewarists feature',
     'https://m.economictimes.com/coke-studio-the-dewarists-non-bollywood-music-shows-original-compositions-gain-traction-in-india/PDAET/articleshow/21748603.cms',
     'Contemporaneous account of the non-film music-show wave and The Dewarists format.'),
    ('dewarists', 'Wikipedia — The Dewarists',
     'https://en.wikipedia.org/wiki/The_Dewarists',
     'Format description: musicians paired to create a new original song.'),
    ('unplugged', 'Wikipedia — MTV Unplugged',
     'https://en.wikipedia.org/wiki/MTV_Unplugged',
     'The acoustic-session format and its editions.'),
    ('tinydesk', 'Wikipedia — Tiny Desk Concerts',
     'https://en.wikipedia.org/wiki/Tiny_Desk_Concerts',
     'Intimate single-take session format, a structural reference for our own sessions.'),
    ('qawwali', 'Wikipedia — Qawwali',
     'https://en.wikipedia.org/wiki/Qawwali',
     'Ensemble form, instruments and its place in South Asian Sufi practice.'),
    ('ghazal', 'Wikipedia — Ghazal',
     'https://en.wikipedia.org/wiki/Ghazal',
     'Origins, structure and the singing tradition.'),
    ('kafi', 'Wikipedia — Kafi',
     'https://en.wikipedia.org/wiki/Kafi',
     'Punjabi and Sindhi devotional verse form.'),
    ('khusrau', 'Wikipedia — Amir Khusrau',
     'https://en.wikipedia.org/wiki/Amir_Khusrau',
     'Poet-musician credited in the qawwali and khayal traditions.'),
    ('bulleh', 'Wikipedia — Bulleh Shah',
     'https://en.wikipedia.org/wiki/Bulleh_Shah',
     'Punjabi Sufi poet of the kafi form.'),
    ('baul', 'Wikipedia — Baul',
     'https://en.wikipedia.org/wiki/Baul',
     'Bengal\'s wandering minstrel tradition.'),
    ('begum', 'Wikipedia — Begum Akhtar',
     'https://en.wikipedia.org/wiki/Begum_Akhtar',
     'Thumri and ghazal gayaki; gharanas she trained in.'),
    ('mehdi', 'Wikipedia — Mehdi Hassan',
     'https://en.wikipedia.org/wiki/Mehdi_Hassan',
     'The classical ghazal voice and its concert lineage.'),
    ('thumri', 'Wikipedia — Thumri',
     'https://en.wikipedia.org/wiki/Thumri',
     'Semi-classical form and its Banaras, Lucknow and Patiala gharanas.'),
    ('navaratri', 'Wikipedia — Navaratri',
     'https://en.wikipedia.org/wiki/Navaratri',
     'The nine-night festival structure our 2026 launch cycle is built around.'),
]

ITEMS = [
    # ---- Sufi ---------------------------------------------------------------
    {'id': 'sufi-qawwali', 'title': 'Qawwali — the mehfil ensemble', 'kind': 'tradition',
     'era': 'heritage', 'region': 'South Asia', 'language': 'Urdu / Punjabi / Persian',
     'summary': 'The best-known South Asian Sufi music form: a lead singer with a chorus, harmonium, tabla and dholak, building a piece through repetition and call-and-response. We keep the ensemble structure and the credit rules; we never import a shrine recording. ' + CONTEXT_ONLY,
     'source_ids': ['qawwali'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'sufi-kafi', 'title': 'Kafi — Punjabi and Sindhi devotional verse', 'kind': 'tradition',
     'era': 'heritage', 'region': 'Punjab / Sindh', 'language': 'Punjabi / Sindhi',
     'summary': 'A sung verse form used across Punjab and Sindh for Sufi poetry, carried by Bulleh Shah and the Sindhi tradition. A kafi cycle sets us a sequence and a theme, not a tune to copy. ' + CONTEXT_ONLY,
     'source_ids': ['kafi', 'bulleh'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'sufi-khusrau', 'title': 'Amir Khusrau — the Persian-Hindavi bridge', 'kind': 'tradition',
     'era': 'heritage', 'region': 'Delhi / South Asia', 'language': 'Persian / Hindavi',
     'summary': 'The poet-musician tradition credits Khusrau with shaping both qawwali practice and the Hindavi-Persian poetic bridge that later ghazal and khayal singing inherit. History and attribution, not a text we reuse. ' + CONTEXT_ONLY,
     'source_ids': ['khusrau', 'qawwali'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'sufi-mehfil', 'title': 'Mehfil and sama — the listening gathering', 'kind': 'tradition',
     'era': 'heritage', 'region': 'South Asia', 'language': 'Urdu / Hindi',
     'summary': 'The gathering format around the music: a sequence that opens with praise, moves through poetry, and closes on repetition, with the audience inside the performance rather than in front of it. This is the structure our original mehfil programme borrows. ' + CONTEXT_ONLY,
     'source_ids': ['qawwali'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'sufi-rock', 'title': 'Sufi rock and fusion — the modern route', 'kind': 'tradition',
     'era': 'modern', 'region': 'South Asia / diaspora', 'language': 'Urdu / Punjabi',
     'summary': 'From the 1990s onward, bands and producers set devotional poetry inside rock, pop and electronic arrangements, which is how this repertoire reached a new audience. A lineage to document and credit, and a production style we may study for our own recordings. ' + CONTEXT_ONLY,
     'source_ids': ['cs-pak', 'cs-dewarists-et'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'sufi-baul', 'title': 'Baul — Bengal\'s wandering minstrels', 'kind': 'tradition',
     'era': 'heritage', 'region': 'Bengal', 'language': 'Bengali',
     'summary': 'Bengali minstrel singers with ektara and dotara, singing of the divine in the everyday. A distinct regional route into the same devotional material, and a reminder that one Sufi reading is never the only one. ' + CONTEXT_ONLY,
     'source_ids': ['baul'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    # ---- Ghazal -------------------------------------------------------------
    {'id': 'ghazal-form', 'title': 'Ghazal — form and structure', 'kind': 'tradition',
     'era': 'heritage', 'region': 'South Asia / Persia / Arabia', 'language': 'Urdu',
     'summary': 'A poem in couplets with a fixed refrain and rhyme pattern, each couplet standing on its own, which is exactly why a ghazal survives being sung out of order. The grammar our original ghazal cycle is written in. ' + CONTEXT_ONLY,
     'source_ids': ['ghazal'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'ghazal-gharanas', 'title': 'Ghazal gayaki — gharanas and the thumri tie', 'kind': 'tradition',
     'era': 'heritage', 'region': 'North India', 'language': 'Urdu / Hindi',
     'summary': 'Classical ghazal singing carries gharana technique — Banaras, Lucknow and Patiala among the thumri schools — which is why the same couplet sounds different in different hands. Technique families to name and credit, not recordings to reissue. ' + CONTEXT_ONLY,
     'source_ids': ['thumri', 'begum', 'ghazal'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'ghazal-poets', 'title': 'Ghazal poetry — the Urdu line', 'kind': 'tradition',
     'era': 'heritage', 'region': 'South Asia', 'language': 'Urdu / Persian',
     'summary': 'The sung ghazal begins as literature: a line of poets from the Deccani works through the Delhi and Lucknow schools to the twentieth century. We keep the chronology and the attribution, and we commission our own verse rather than republishing theirs. ' + CONTEXT_ONLY,
     'source_ids': ['ghazal', 'khusrau'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'ghazal-begum-akhtar', 'title': 'Begum Akhtar — thumri and ghazal gayaki', 'kind': 'tradition',
     'era': 'heritage', 'region': 'North India', 'language': 'Urdu / Hindi',
     'summary': 'A reference point for how semi-classical technique and recorded ghazal met: trained across more than one gharana, and equally at home in thumri, dadra and ghazal. Studied for phrasing and sequencing; her records stay hers. ' + CONTEXT_ONLY,
     'source_ids': ['begum', 'thumri'], 'artists': ['Begum Akhtar'], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'ghazal-mehdi-hassan', 'title': 'Mehdi Hassan — the classical concert ghazal', 'kind': 'tradition',
     'era': 'heritage', 'region': 'South Asia', 'language': 'Urdu',
     'summary': 'The concert stage where classical ghazal gayaki reached a mass audience, and the reference for how a long programme holds a hall. A model for programme shape, with every recording credited to its own rights holders. ' + CONTEXT_ONLY,
     'source_ids': ['mehdi', 'ghazal'], 'artists': ['Mehdi Hassan'], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'ghazal-now', 'title': 'Ghazal today — records, television and the mehfil revival', 'kind': 'tradition',
     'era': 'modern', 'region': 'South Asia / diaspora', 'language': 'Urdu / Hindi',
     'summary': 'How the form travelled — shellac-era records, the film and television ghazal, then the concert and festival circuit and the small-room revival. The route map for our own cycle, with no recording rehosted at any stop. ' + CONTEXT_ONLY,
     'source_ids': ['ghazal', 'mehdi'], 'artists': [], 'year': None, 'record_type': 'format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    # ---- Studio and show formats -------------------------------------------
    {'id': 'show-coke-studio-pk', 'title': 'Coke Studio Pakistan — house band and guest artists (from 2008)', 'kind': 'video',
     'era': 'modern', 'region': 'Pakistan', 'language': 'Urdu / Punjabi / regional',
     'summary': 'The format we are learning from: a house band with guest artists, recorded live in a studio, season by season under a named producer. The cited account lists the first season in 2008 and fifteen seasons by the check date, with production passing from its founders to later producers. Format and history only. ' + CONTEXT_ONLY,
     'source_ids': ['cs-pak'], 'artists': [], 'year': 2008, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-coke-studio-franchise', 'title': 'The Coke Studio format beyond Pakistan — India, Bangla, Bel 3arabi', 'kind': 'video',
     'era': 'modern', 'region': 'South Asia / Middle East / Brazil origin', 'language': 'Multiple',
     'summary': 'The same studio-collaboration idea in other countries: the Pakistani edition began in 2008, India in 2011, an Arabic edition in 2012 and a Bengali edition in 2022, with the concept traced back to a Brazilian project in 2007. A comparative map of how one format adapts to a language and a market. ' + CONTEXT_ONLY,
     'source_ids': ['cs-franchise', 'cs-bangla', 'cs-pak'], 'artists': [], 'year': 2007, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-coke-studio-india', 'title': 'Coke Studio India — 2011 launch and the regional variants', 'kind': 'video',
     'era': 'modern', 'region': 'India', 'language': 'Hindi / regional',
     'summary': 'The Indian edition opened in 2011 with a first season of long-form episodes and a television tie-in, then returned in several different shapes and, later, regional editions. Evidence that an Indian-language version of this format is viable - and that it needs its own identity rather than an imported one. ' + CONTEXT_ONLY,
     'source_ids': ['cs-franchise', 'cs-dewarists-et'], 'artists': [], 'year': 2011, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-coke-studio-bangla', 'title': 'Coke Studio Bangla — a language-first edition (2022)', 'kind': 'video',
     'era': 'modern', 'region': 'Bangladesh', 'language': 'Bengali',
     'summary': 'The Bengali edition launched in 2022 and is the closest recent example of the format being rebuilt around one language and its own musicians rather than translated into it. The model we intend to follow for Hindi and Marathi. ' + CONTEXT_ONLY,
     'source_ids': ['cs-bangla'], 'artists': [], 'year': 2022, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-mtv-unplugged', 'title': 'MTV Unplugged — the acoustic session format', 'kind': 'video',
     'era': 'modern', 'region': 'Global / India', 'language': 'Multiple',
     'summary': 'An artist plays their own material with acoustic arrangements in a controlled room: no spectacle, performance front and centre, and editions localised per country. A low-risk format for our first recorded sessions, because it needs a room and a band, not a set. ' + CONTEXT_ONLY,
     'source_ids': ['unplugged', 'cs-dewarists-et'], 'artists': [], 'year': None, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-dewarists', 'title': 'The Dewarists — collaboration as documentary', 'kind': 'video',
     'era': 'modern', 'region': 'India', 'language': 'Hindi / English',
     'summary': 'Two musicians from different traditions are paired to write and record something new, and the episode documents the process as much as the song; its makers describe it as part music documentary, part travelogue. The closest structural ancestor to what we want our original collaborations to be. ' + CONTEXT_ONLY,
     'source_ids': ['dewarists', 'cs-dewarists-et'], 'artists': [], 'year': 2011, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-tinydesk', 'title': 'Tiny Desk Concerts — the intimate single-take session', 'kind': 'video',
     'era': 'modern', 'region': 'United States', 'language': 'English / multiple',
     'summary': 'One small space, one continuous performance, the artist choosing the set: proof that a music programme needs no studio budget to travel. The template for the first Vyomaraj sessions, scaled to a room we actually have. ' + CONTEXT_ONLY,
     'source_ids': ['tinydesk'], 'artists': [], 'year': None, 'record_type': 'show format',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    {'id': 'show-rules', 'title': 'What we may inherit from these shows — and what we may not', 'kind': 'video',
     'era': 'cross-era', 'region': 'South Asia / global', 'language': 'English / Hindi',
     'summary': 'Format, structure, sequencing and production method are reference material. Titles, lyrics, audio, video, artwork, logos and episode content are never copied, and nothing is rehosted. Any future licensed use requires a written licence naming the rights holder. Every card in this group follows that rule, and so does every plan the planner can build from it. ' + CONTEXT_ONLY,
     'source_ids': ['cs-pak', 'cs-franchise'], 'artists': [], 'year': None, 'record_type': 'rights rule',
     'media_url': None, 'licence_status': 'not_licensed_for_rehosting', 'explicit_status': 'not_reviewed'},
    # ---- Original programme formats (ours, nothing borrowed) ----------------
    {'id': 'original-mehfil-sessions', 'title': 'Original: Mehfil Sessions — our own gathering format', 'kind': 'audio',
     'era': 'cross-era', 'region': 'India', 'language': 'Hindi / Urdu',
     'summary': 'The first original programme in this lane: a four-part gathering that opens with praise, moves through poetry and closes on repetition, with an original scripted link at every step and a source line for every reference. Built on the mehfil structure above; it contains no borrowed verse, melody or recording.',
     'source_ids': ['qawwali'], 'artists': [], 'year': 2026, 'record_type': 'original programme',
     'media_url': None, 'licence_status': ORIGINAL, 'explicit_status': 'original_creator_owned',
     'rights_basis': 'Original script, sequence and links written for Vyomaraj and credited to named creators before release; no third-party work is sampled, adapted or rehosted.'},
    {'id': 'original-sufi-cycle', 'title': 'Original: Sufi Cycle — nine nights of devotional programming', 'kind': 'audio',
     'era': 'cross-era', 'region': 'India', 'language': 'Hindi / Urdu / Punjabi',
     'summary': 'Nine original programmes, one per night, each taking a single devotional theme through poetry, commentary and an original composition, with regional variants (Punjabi kafi, Bengali Baul, Deccan) night by night. Written for Vyomaraj; nothing existing is performed or reissued.',
     'source_ids': ['kafi', 'baul'], 'artists': [], 'year': 2026, 'record_type': 'original programme',
     'media_url': None, 'licence_status': ORIGINAL, 'explicit_status': 'original_creator_owned',
     'rights_basis': 'Original compositions and scripts to be written, credited and recorded by named Vyomaraj creators; no existing composition, lyric or recording is used.'},
    {'id': 'original-ghazal-cycle', 'title': 'Original: Ghazal Cycle — new verse in the mehfil setting', 'kind': 'audio',
     'era': 'cross-era', 'region': 'India', 'language': 'Urdu / Hindi',
     'summary': 'A ghazal programme built the other way round from a covers show: the verse is written first for Vyomaraj, then set and sung, with credit for poet, composer and performer on every piece. The classical forms above are the grammar, not the material.',
     'source_ids': ['ghazal'], 'artists': [], 'year': 2026, 'record_type': 'original programme',
     'media_url': None, 'licence_status': ORIGINAL, 'explicit_status': 'original_creator_owned',
     'rights_basis': 'Original verse and compositions commissioned for Vyomaraj with named writers, credited before release; no existing couplet, melody or recording is used.'},
    {'id': 'original-navaratri-cycle', 'title': 'Original: Navaratri 2026 cycle — nine nights, one programme each', 'kind': 'audio',
     'era': 'modern', 'region': 'India', 'language': 'Hindi / Marathi / English',
     'summary': 'The launch programming for the Navaratri window that opens on Ghatasthapana, 11 October 2026, and closes at Vijayadashami on 20 October 2026: nine original programmes, one per night, each pairing a devotional theme with a music or ghazal set and its own credits. Ties the bhakti lane to this one, and is the programme the 11 October live run is meant to open with.',
     'source_ids': ['navaratri'], 'artists': [], 'year': 2026, 'record_type': 'original programme',
     'media_url': None, 'licence_status': ORIGINAL, 'explicit_status': 'original_creator_owned',
     'rights_basis': 'Original programme plan, scripts and compositions produced by Vyomaraj for the 2026 Navaratri window; festival timing follows public almanac references, and no third-party work is used.'},
]

BACKLOG = [
    'Record the gharana and technique notes behind the ghazal cards with a named reviewer before any of it is taught or published.',
    'Decide, with the owner, whether the first Mehfil Sessions are audio-only or filmed, and pick the room: that choice fixes the whole launch production plan.',
    'Do not publish any Sufi or ghazal card as a performance before the original recordings exist and their creators are credited by name.',
]

EXTENSION = {
    'added_on': UPDATED,
    'requested_by': 'owner',
    'request': 'Research, update, modify, integrate and inherit all contents, new and old, of Sufi, Ghazal, Coke Studio and its similar shows.',
    'new_items': len(ITEMS),
    'groups': {'sufi': 6, 'ghazal': 6, 'studio_and_show_formats': 8, 'original_programmes': 4},
    'inheritance_rule': ('Inherit the format, the structure and the credit discipline. Never the '
                         'titles, lyrics, audio, video, artwork, brands or episode content.'),
    'heritage_items_are_context_only': True,
    'media_rehosted': False,
    'episodes_imported': False,
    'lyrics_imported': False,
    'brand_assets_used': False,
    'original_programmes_have_own_rights_basis': True,
    'agents_created': 0,
    'registry_totals_changed': False,
    'bindings': 'existing ENT-MUS-S3 (folk, regional and world), ENT-MUS-S5 (audio programming), ENT-MUS-S6 (music video and visual programmes)',
    'navaratri_window': {'Ghatasthapana': '2026-10-11', 'Vijayadashami': '2026-10-20',
                         'source': 'public almanac references cited in this pack; the owner\'s live date is the first night'},
}


def load():
    return json.loads(PACK.read_text(encoding='utf-8'))


def apply(data):
    ids = {item['id'] for item in data['items']}
    clashes = [item['id'] for item in ITEMS if item['id'] in ids]
    if clashes:
        raise SystemExit(f'item ids already present: {clashes}')
    known = {source['id'] for source in data['sources']}
    added_sources, skipped = [], []
    for sid, title, url, basis in SOURCES:
        if sid in known:
            skipped.append(sid)
            continue
        added_sources.append({'id': sid, 'title': title, 'url': url, 'citation': f'[1]({url})',
                              'checked': UPDATED,
                              'review_basis': f'{basis} Reference check; format and history metadata only, not a full-text review.'})
    if skipped:
        raise SystemExit(f'source ids already present: {skipped}')
    data['sources'] = data['sources'] + added_sources
    data['items'] = data['items'] + ITEMS
    data['backlog'] = data['backlog'] + BACKLOG
    data['extension_2026_10_06'] = EXTENSION
    data['updated'] = UPDATED
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify the pack; never write')
    args = parser.parse_args()
    data = load()
    if data.get('extension_2026_10_06'):
        print(f"OK: pack already carries the {UPDATED} extension "
              f"({len(data['items'])} starter cards, {len(data['sources'])} sources)")
        return
    apply(data)
    if args.check:
        raise SystemExit('FAIL: pack does not carry the extension yet; run without --check')
    PACK.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    extensions = json.loads(EXTENSIONS.read_text(encoding='utf-8'))
    for entry in extensions['extensions']:
        if entry['id'] == 'music-memory-melody':
            entry['sufi_ghazal_show_formats_added'] = len(ITEMS)
            entry['original_programmes_added'] = EXTENSION['groups']['original_programmes']
            entry['heritage_items_are_context_only'] = True
            entry['media_rehosted'] = False
            entry['updated'] = UPDATED
    extensions['updated'] = UPDATED
    EXTENSIONS.write_text(json.dumps(extensions, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"wrote {PACK.relative_to(ROOT)} — {len(data['items'])} starter cards, "
          f"{len(data['sources'])} sources, {len(ITEMS)} added")
    print(f"wrote {EXTENSIONS.relative_to(ROOT)} — extension entry annotated")


if __name__ == '__main__':
    main()
