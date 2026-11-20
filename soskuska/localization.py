"""Explicit UI-only translation; no Tk, networking or process locale changes."""
import json
import re
from pathlib import Path
from string import Formatter

LANGUAGE_CODES = {'English':'en','Czech':'cs','Slovak':'sk','Russian':'ru'}
LANGUAGE_NAMES = {'English':'English','Czech':'Čeština','Slovak':'Slovenčina','Russian':'Русский'}


def fields(text):
    return {name for _,name,_,_ in Formatter().parse(text) if name is not None}


class Translator:
    def __init__(self, language='English'):
        self.language = language if language in LANGUAGE_CODES else 'English'
        self.catalog = json.loads((Path(__file__).with_name('i18n')/(LANGUAGE_CODES[self.language]+'.json')).read_text(encoding='utf-8'))
        self.patterns = []
        if self.language!='English':
            for source,target in self.catalog.items():
                pieces=list(Formatter().parse(source))
                if not any(name is not None for _,name,_,_ in pieces):continue
                literal_size=sum(len(literal) for literal,_,_,_ in pieces)
                if literal_size<5:continue
                pattern='';names=set()
                for literal,name,_,_ in pieces:
                    pattern+=re.escape(literal)
                    if name is not None:
                        pattern+=f'(?P<{name}>.*?)' if name not in names else f'(?P={name})'
                        names.add(name)
                self.patterns.append((literal_size,re.compile('^'+pattern+'$',re.S),target))
            self.patterns.sort(key=lambda item:item[0],reverse=True)

    def text(self, source, **values):
        if not isinstance(source,str):return source
        if not values and self.language!='English':
            record=re.fullmatch(r'CSV record (\d+): (.*)',source,re.S)
            if record:
                return self.text('CSV record {v0}: {v1}',v0=record[1],v1=self.text(record[2]))
        target=self.catalog.get(source)
        if values:
            return (target or source).format(**values)
        if target is not None:return target
        # Backend errors may already contain formatted details. Capture them as
        # opaque values; translate only the surrounding explicitly cataloged copy.
        for _,pattern,template in self.patterns:
            match=pattern.fullmatch(source)
            if match:
                return ''.join(literal+(match.group(name) if name is not None else '') for literal,name,_,_ in Formatter().parse(template))
        return source  # Technical errors and unknown future copy remain readable.


def tr(owner, source, **values):
    translator=getattr(owner,'__dict__',{}).get('translator')
    if isinstance(translator,Translator):return translator.text(source,**values)
    return source.format(**values) if values else source


def duration_text(owner, value):
    """Translate display units only; retain canonical storage/scheduler strings."""
    translator=getattr(owner,'__dict__',{}).get('translator')
    if not isinstance(translator,Translator) or translator.language!='Russian':return value
    return re.sub(r'(\d)([hmsd])',lambda m:m[1]+{'h':'ч','m':'м','s':'с','d':'д'}[m[2]],value)
