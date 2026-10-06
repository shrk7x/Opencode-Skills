#!/usr/bin/env python3
"""Extract EPUB text evidence. Candidate flags are not acceptance verdicts."""
import argparse
import json
import posixpath
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET


def local(tag):
    return tag.rsplit('}', 1)[-1]


class BodyText(HTMLParser):
    breaks = {'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'pre', 'dt', 'dd', 'td'}
    voids = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.blocks = []
        self.parts = []
        self.in_body = False

    def flush(self):
        text = ' '.join(''.join(self.parts).split())
        if text:
            self.blocks.append({'index': len(self.blocks) + 1, 'text': text, 'chars': len(text)})
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        style = re.sub(r'\s+', '', attrs.get('style', '').lower())
        hidden = (tag in {'script', 'style', 'template'} or 'hidden' in attrs
                  or 'display:none' in style or 'visibility:hidden' in style)
        hidden = hidden or bool(self.stack and self.stack[-1][1])
        if tag == 'body':
            self.in_body = True
        if self.in_body and tag in self.breaks:
            self.flush()
        if tag == 'br' and self.in_body and not hidden:
            self.parts.append(' ')
        if tag not in self.voids:
            self.stack.append((tag, hidden))

    def handle_endtag(self, tag):
        if self.in_body and (tag in self.breaks or tag == 'body'):
            self.flush()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]
                break
        if tag == 'body':
            self.in_body = False

    def handle_data(self, data):
        if self.in_body and not (self.stack and self.stack[-1][1]):
            self.parts.append(data)


def resolve(base, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        raise ValueError('External EPUB resource: ' + href)
    path = posixpath.normpath(posixpath.join(posixpath.dirname(base), unquote(parsed.path)))
    if path.startswith('../') or path.startswith('/'):
        raise ValueError('Invalid EPUB resource path: ' + href)
    return path


def read_epub(path):
    documents = []
    with zipfile.ZipFile(path) as z:
        container = ET.fromstring(z.read('META-INF/container.xml'))
        roots = [e.attrib['full-path'] for e in container.iter() if local(e.tag) == 'rootfile']
        if not roots:
            raise ValueError('No OPF rootfile')
        opf_path = roots[0]
        opf = ET.fromstring(z.read(opf_path))
        manifest = {e.attrib['id']: e.attrib for e in opf.iter() if local(e.tag) == 'item'}
        spine = [e.attrib for e in opf.iter() if local(e.tag) == 'itemref']
        ordered = [(manifest[e['idref']], True, e.get('linear', 'yes')) for e in spine]
        used = {e['idref'] for e in spine}
        ordered += [(item, False, 'no') for key, item in manifest.items() if key not in used]
        for item, in_spine, linear in ordered:
            href = item.get('href', '')
            if item.get('media-type') not in {'application/xhtml+xml', 'text/html'} and not urlsplit(href).path.lower().endswith(('.html', '.htm', '.xhtml')):
                continue
            name = resolve(opf_path, href)
            raw = z.read(name)
            encoding = re.search(br'encoding\s*=\s*[\'"]([^\'"]+)', raw[:200])
            text = raw.decode(encoding.group(1).decode('ascii') if encoding else 'utf-8-sig')
            parser = BodyText()
            parser.feed(text)
            parser.flush()
            documents.append({'path': name, 'in_spine': in_spine, 'linear': linear,
                              'properties': item.get('properties', ''), 'blocks': parser.blocks,
                              'chars': sum(b['chars'] for b in parser.blocks)})
    if not documents or not any(d['chars'] for d in documents):
        raise ValueError('No readable body text; cannot verify this EPUB')
    return {'file': str(Path(path).resolve()), 'documents': documents}


def normalized(text):
    return ' '.join(text.split()).casefold()


def compare(original, translated):
    flags = []
    target = {d['path']: d for d in translated['documents']}
    source_blocks = {}
    for doc in original['documents']:
        for block in doc['blocks']:
            if block['chars'] >= 300:
                source_blocks.setdefault(normalized(block['text']), []).append({'path': doc['path'], 'block': block['index']})
        if doc['chars'] < 300:
            continue
        match = target.get(doc['path'])
        if match is None:
            flags.append({'kind': 'missing_document_candidate', 'source_path': doc['path']})
        elif match['chars'] < doc['chars'] * .4:
            flags.append({'kind': 'short_document_candidate', 'path': doc['path'],
                          'source_chars': doc['chars'], 'translated_chars': match['chars']})
    for doc in translated['documents']:
        for block in doc['blocks']:
            key = normalized(block['text'])
            if key in source_blocks:
                flags.append({'kind': 'unchanged_long_block', 'path': doc['path'], 'block': block['index'],
                              'source_matches': source_blocks[key]})
    return flags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path)
    parser.add_argument('--translated', required=True, type=Path)
    parser.add_argument('--target-language', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        translated = read_epub(args.translated)
        original = read_epub(args.original) if args.original else None
        report = {'target_language': args.target_language, 'verdict': 'requires_review',
                  'original_available': original is not None,
                  'candidates': compare(original, translated) if original else [],
                  'note': 'All HTML resources included. Review body scope, actual language, and candidate flags before deciding.'}
        for key, book in [('original', original), ('translated', translated)]:
            report[key] = [{'path': d['path'], 'in_spine': d['in_spine'], 'chars': d['chars'],
                            'blocks': len(d['blocks'])} for d in book['documents']] if book else None
        args.out.mkdir(parents=True, exist_ok=False)
        for name, value in [('original', original), ('translated', translated), ('report', report)]:
            if value is not None:
                (args.out / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
        print(args.out.resolve() / 'report.json')
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        parser.exit(2, 'Cannot inspect EPUB: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
