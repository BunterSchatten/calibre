#!/usr/bin/env python
# License: GPLv3 Copyright: 2017, Kovid Goyal <kovid at kovidgoyal.net>


from calibre.srv.changes import BooksAdded, BooksDeleted, FormatsAdded, FormatsRemoved, MetadataChanged, SavedSearchesChanged


def handle_changes(changes, gui=None):
    if not changes:
        return
    if gui is None:
        from calibre.gui2.ui import get_gui
        gui = get_gui()
    if gui is None:
        return
    refresh_ids = set()
    added, removed = set(), set()
    ss_changed = False
    for change in changes:
        if isinstance(change, (FormatsAdded, FormatsRemoved, MetadataChanged)):
            refresh_ids |= change.book_ids
        elif isinstance(change, BooksAdded):
            added |= change.book_ids
        elif isinstance(change, BooksDeleted):
            removed |= change.book_ids
        elif isinstance(change, SavedSearchesChanged):
            ss_changed = True

    if added and removed:
        gui.refresh_all()
        return
    refresh_ids -= added | removed
    orig = gui.tags_view.disable_recounting, gui.disable_cover_browser_refresh
    gui.tags_view.disable_recounting = gui.disable_cover_browser_refresh = True
    position_based_recount = True
    try:
        if added:
            gui.current_db.data.books_added(added)
            gui.iactions['Add Books'].refresh_gui(len(added), recount=False)
            position_based_recount = False
        if removed:
            next_id = gui.current_view().next_id
            m = gui.library_view.model()
            m.ids_deleted(removed)
            gui.iactions['Remove Books'].library_ids_deleted2(removed, next_id=next_id)
        if refresh_ids:
            gui.iactions['Edit Metadata'].refresh_books_after_metadata_edit(refresh_ids)
        if ss_changed:
            gui.saved_searches_changed(recount=False)
        gui.tags_view.disable_recounting = gui.disable_cover_browser_refresh = False
        (gui.tags_view.recount_with_position_based_index if position_based_recount else gui.tags_view.recount)()
        gui.refresh_cover_browser()
    finally:
        gui.tags_view.disable_recounting, gui.disable_cover_browser_refresh = orig
