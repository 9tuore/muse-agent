#!/usr/bin/env python3
"""Sync modules into the readable entry; compact/sign the delivery bundle afterwards."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'official_muse/app/source/main.splash'
text=path.read_text()
if '// BEGIN STORAGE_IO\n' not in text:
 text='// BEGIN STORAGE_IO\n// END STORAGE_IO\n\n'+text
if '// BEGIN ACTIVITY_ARCHIVE\n' not in text:
 anchor='let core_last_activity = ""'
 index=text.index(anchor)+len(anchor)
 text=text[:index]+'\n\n// BEGIN ACTIVITY_ARCHIVE\n// END ACTIVITY_ARCHIVE'+text[index:]
if '// BEGIN INCOMING_MAIL\n' not in text:
 a=text.index('// Inbox polling uses only granted Host accounts.')
 b=text.index('fn mail_redraw(',a)
 text=text[:a]+'// BEGIN INCOMING_MAIL\n'+text[a:b].rstrip()+'\n// END INCOMING_MAIL\n\n'+text[b:]
for marker,source in [('STORAGE_IO','storage_io.splash'),('ACTIVITY_ARCHIVE','activity_archive.splash'),('GLOBAL_MEMORY','global_memory.splash'),('UI_PAGE_ADAPTERS','ui_page_adapters.splash'),('INCOMING_MAIL','incoming_mail.splash')]:
 start='// BEGIN '+marker+'\n';end='// END '+marker
 assert text.count(start)==text.count(end)==1, marker
 a=text.index(start)+len(start);b=text.index(end,a)
 text=text[:a]+(ROOT/'official_muse'/source).read_text().rstrip()+'\n'+text[b:]
path.write_text(text)
