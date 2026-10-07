#!/usr/bin/env python3
"""Deterministic retrieval over the current catalog — retrieval, not generation.

The catalog is exactly two checked-in files:

  * ``AGENT_REGISTRY_CURRENT.json``   — the 133 counted positions plus the 6 uncounted
    parent headings of the current owner-approved hierarchy.
  * ``CONTENT_INDEX_CURRENT.json``    — the 197 indexed content references.

This module answers a question by *selecting* rows from those files and citing them.
It never writes a title, name or record that is not already in the data:

  * unnamed positions are returned as serial-only slots (the display policy of the
    registry forbids inventing names);
  * a query whose tokens do not all match a record returns no results rather than a
    nearest guess;
  * every result carries a citation (file + pointer) that a reader can open.

There is no model call and no network access here. That is the honest state of the
slice: the retrieval seam a generation step would sit behind is ``ask()``.
"""
import json
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY_PATH = HERE / 'AGENT_REGISTRY_CURRENT.json'
INDEX_PATH = HERE / 'CONTENT_INDEX_CURRENT.json'

# Navigation aliases only. They widen the words a *visitor* may type; they are not
# catalog data and can never create a result by themselves (a document still has to
# exist and match the query's own tokens too).
ALIASES = {
    'govt': ('government',),
    'yojana': ('scheme', 'government'),
    'gita': ('geeta', 'bhagavad'),
    'geeta': ('gita',),
    'bhagavad': ('gita',),
    'film': ('movie', 'cinema', 'screen'),
    'films': ('movie', 'cinema', 'screen'),
    'movie': ('film', 'cinema'),
    'cinema': ('film', 'movie'),
    'music': ('song', 'audio'),
    'song': ('music',),
    'gaana': ('music', 'song'),
    'cartoon': ('comics', 'animation'),
    'comics': ('cartoon',),
    'comedy': ('hasya', 'wit'),
    'hasya': ('comedy',),
    'shayari': ('poetry',),
    'poetry': ('shayari',),
}

_FIELDS = (
    ('title_exact', 100),
    ('title', 40),
    ('parent', 30),
    ('category', 15),
    ('id', 12),
    ('reference', 8),
)


def singular(token):
    """Plural-insensitive comparison key: 'schemes' and 'scheme' are one word."""
    return token[:-1] if len(token) > 3 and token.endswith('s') else token


def same_word(left, right):
    return left == right or singular(left) == singular(right)


def fold(text):
    """Lower-case, strip accents/punctuation so 'Gītā' and 'gita' are the same token."""
    if text is None:
        return ''
    text = unicodedata.normalize('NFKD', str(text))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def tokens(text):
    folded = fold(text)
    return tuple(dict.fromkeys(t for t in folded.split(' ') if t))


class Catalog:
    """Loads the two source files and answers questions with cited rows."""

    def __init__(self, registry_path=REGISTRY_PATH, index_path=INDEX_PATH):
        self.registry_path = Path(registry_path)
        self.index_path = Path(index_path)
        self.registry = json.loads(self.registry_path.read_text(encoding='utf-8'))
        self.index = json.loads(self.index_path.read_text(encoding='utf-8'))
        self.categories = {c['id']: c for c in self.registry['categories']}
        self.heading_names = {h['id']: h['name'] for h in self.registry.get('headings', [])}
        self._documents = None

    # ------------------------------------------------------------------ data

    def _position_document(self, agent):
        category = self.categories.get(agent['category_id'], {})
        named = bool(agent.get('name'))
        title = agent['name'] if named else None
        display = title if named else f"UNNAMED SLOT {agent['id']} (serial {agent['serial']})"
        parent_name = self.heading_names.get(agent.get('parent_id'), '')
        fields = {
            'title': title or '',
            'id': agent['id'],
            'parent': parent_name,
            'category': f"{category.get('name', '')} {agent['category_id']}",
            'reference': '',
        }
        return {
            'kind': 'position',
            'id': agent['id'],
            'title': title,
            'display': display,
            'name_status': agent.get('name_status'),
            'named': named,
            'category_id': agent['category_id'],
            'category_name': category.get('name'),
            'serial': agent['serial'],
            'parent_id': agent.get('parent_id'),
            'counted': agent.get('counted', True),
            'citation': f"{self.registry_path.name}#/agents/{agent['id']}",
            'fields': fields,
        }

    def _heading_document(self, heading):
        category = self.categories.get(heading['category_id'], {})
        return {
            'kind': 'heading',
            'id': heading['id'],
            'title': heading['name'],
            'display': heading['name'],
            'named': True,
            'category_id': heading['category_id'],
            'category_name': category.get('name'),
            'counted': False,
            'citation': f"{self.registry_path.name}#/headings/{heading['id']}",
            'fields': {
                'title': heading['name'],
                'id': heading['id'],
                'parent': '',
                'category': f"{category.get('name', '')} {heading['category_id']}",
                'reference': '',
            },
        }

    def _reference_document(self, record):
        category = self.categories.get(record.get('owner_category'), {})
        refs = record.get('source_refs') or []
        reference_text = ' '.join(f"{r.get('path', '')} {r.get('locator', '')}" for r in refs)
        return {
            'kind': 'content_reference',
            'id': record['id'],
            'title': record['title'],
            'display': record['title'],
            'named': True,
            'category_id': record.get('owner_category'),
            'category_name': category.get('name', record.get('owner_category')),
            'record_kind': record.get('kind'),
            'source_refs': refs,
            'full_content_imported': record.get('full_content_imported', False),
            'citation': f"{self.index_path.name}#/records/{record['id']}",
            'fields': {
                'title': record['title'],
                'id': record['id'],
                'parent': '',
                'category': f"{category.get('name', '')} {record.get('owner_category', '')}",
                'reference': reference_text,
            },
        }

    def documents(self):
        if self._documents is None:
            docs = [self._position_document(a) for a in self.registry['agents']]
            docs += [self._heading_document(h) for h in self.registry.get('headings', [])]
            docs += [self._reference_document(r) for r in self.index['records']]
            for doc in docs:
                doc['fields'] = {key: fold(value) for key, value in doc['fields'].items()}
            self._documents = docs
        return self._documents

    def stats(self):
        agents = self.registry['agents']
        kinds = {}
        for record in self.index['records']:
            kinds[record.get('kind', 'unknown')] = kinds.get(record.get('kind', 'unknown'), 0) + 1
        return {
            'categories': len(self.registry['categories']),
            'positions': len(agents),
            'named_positions': sum(1 for a in agents if a.get('name')),
            'unnamed_positions': sum(1 for a in agents if not a.get('name')),
            'headings_uncounted': len(self.registry.get('headings', [])),
            'content_references': len(self.index['records']),
            'content_reference_kinds': dict(sorted(kinds.items())),
            'registry_file': self.registry_path.name,
            'index_file': self.index_path.name,
            'generation': 'none — retrieval only, no model call',
        }

    # ------------------------------------------------------------------ query

    @staticmethod
    def _evidence(fields, term):
        """Best evidence for one term in one document, or None when it does not match."""
        found = None
        for label, weight in _FIELDS:
            value = fields.get(label, '')
            if not value:
                continue
            if term == value:
                matched = weight + 60
            elif any(same_word(term, word) for word in value.split(' ')):
                matched = weight
            elif label == 'title' and len(term) >= 4 and term in value:
                matched = weight - 12
            else:
                continue
            if found is None or matched > found[1]:
                found = (label, matched)
        return found

    def ask(self, query, limit=10):
        """Return cited rows for a query. No match returns an empty list, never a guess."""
        limit = max(1, min(int(limit), 50))
        query_tokens = tokens(query)
        result = {
            'query': query,
            'query_tokens': list(query_tokens),
            'aliases_applied': {},
            'considered': len(self.documents()),
            'matches': 0,
            'returned': 0,
            'results': [],
            'note': None,
        }
        if not query_tokens:
            result['note'] = 'empty query — nothing to look up'
            return result

        expansions = {}
        for token in query_tokens:
            equivalents = tuple(dict.fromkeys((token,) + ALIASES.get(token, ())))
            expansions[token] = equivalents
            result['aliases_applied'][token] = list(equivalents[1:])

        matches = []
        used_aliases = {}
        for doc in self.documents():
            total = 0
            evidence = []
            rejected = False
            for token, equivalents in expansions.items():
                best = None
                for term in equivalents:
                    found = self._evidence(doc['fields'], term)
                    if found is None:
                        continue
                    label, weight = found
                    if term != token:
                        label, weight = f"alias:{term}->{label}", int(weight * 0.6)
                    if best is None or weight > best[1]:
                        best = (label, weight, term)
                if best is None:
                    rejected = True
                    break
                total += best[1]
                evidence.append({'token': token, 'matched': best[0], 'weight': best[1]})
                if best[0].startswith('alias:'):
                    used_aliases.setdefault(token, set()).add(best[2])
            if rejected:
                continue
            if doc['kind'] == 'position' and doc['named']:
                total += 5
            matches.append((total, doc, evidence))

        matches.sort(key=lambda row: (-row[0], row[1]['kind'], row[1]['id']))
        result['aliases_applied'] = {token: sorted(values) for token, values in sorted(used_aliases.items())}
        result['matches'] = len(matches)
        for rank, (score, doc, evidence) in enumerate(matches[:limit], start=1):
            entry = {
                'rank': rank,
                'kind': doc['kind'],
                'id': doc['id'],
                'title': doc['title'],
                'display': doc['display'],
                'category_id': doc['category_id'],
                'category_name': doc['category_name'],
                'citation': doc['citation'],
                'score': score,
                'matched_terms': [e['matched'] for e in evidence],
            }
            if doc['kind'] == 'position':
                entry['serial'] = doc['serial']
                entry['counted'] = doc['counted']
                entry['named'] = doc['named']
            elif doc['kind'] == 'heading':
                entry['counted'] = False
            else:
                entry['record_kind'] = doc['record_kind']
                entry['source_refs'] = doc['source_refs']
                entry['full_content_imported'] = doc['full_content_imported']
            result['results'].append(entry)
        result['returned'] = len(result['results'])
        if not matches:
            result['note'] = ('no record in the 133 positions or 197 content references matches '
                              'every word of this query — nothing is invented to fill the gap')
        elif len(matches) > limit:
            result['note'] = f'{len(matches)} matching records; showing the top {limit}'
        return result


def ask(query, limit=10):
    """Convenience for one-shot use; callers that ask repeatedly should keep a Catalog."""
    return Catalog().ask(query, limit=limit)
