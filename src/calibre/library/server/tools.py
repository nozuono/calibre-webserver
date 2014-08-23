#!/usr/bin/calibre-debug
#-*- coding: UTF-8 -*-

import logging, douban
from calibre.db.legacy import LibraryDatabase

def update_all_by_isbn(library_path):
    def do_book_update(id):
        book_id = int(id)
        mi = db.get_metadata(book_id, index_is_id=True)
        douban_mi = douban.get_douban_metadata(mi)
        if not douban_mi:
            logging.error("-- erro %d" % book_id)
            raise
        if mi.cover_data[0]:
            douban_mi.cover_data = None
        mi.smart_update(douban_mi, replace_metadata=True)
        db.set_metadata(book_id, mi)
        logging.error("** done %d" % book_id)

    db = LibraryDatabase(os.path.expanduser(library_path))
    ids = db.search_getting_ids('', None)
    for i in ids:
        if i < 2837: continue
        try: do_book_update(i)
        except: pass
    return 0

if __name__ == '__main__':
    update_all_by_isbn(sys.argv[1])


