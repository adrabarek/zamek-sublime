import sublime
import sublime_plugin
import os
import glob
import pickle
import pprint
import datetime

from collections import namedtuple

CONFIG_PATH = os.path.expanduser("~/.zamek")
REGISTRY_PATH = os.path.join(CONFIG_PATH, "registry")
NOTE_EXTENSION = ".zamek"

Note = namedtuple('Note', ['path', 'name', 'links', 'tags'])


def note_name_from_path(path):
    (result, _) = os.path.splitext(os.path.basename(path))
    return result


def split_line(line):
    return list(
        filter(
            lambda x: x != "", [
                x.strip() for x in line.split(',')]))


def split_list(prefix, text_lines):
    # Checks text_lines for line in form "prefix: a, b, c"
    # If found, returns ["a", "b", "c"].

    for line in text_lines:
        split = line.split(':')
        if split[0] == prefix:
            result = split_line(split[1])
            return result

    return []


def note_from_path(path):
    links = set([])
    tags = set([])
    if os.path.exists(path):
        lines = []
        with open(path, "r") as file:
            lines = file.readlines()
        links = set(split_list("links", lines))
        tags = set(split_list("tags", lines))
    else:
        tags = set([])
        links = set([])

    return Note(path=path, name=note_name_from_path(path),
                links=links, tags=tags)


def update_note_text(note, note_text=None):
    lines = []
    if not note_text:
        with open(note.path, "r") as file:
            lines = file.readlines()
    else:
        lines = note_text.split('\n')

    for i, line in enumerate(lines):
        split = line.split(":")

        if split[0] == "links":
            line = "links: "
            for link in note.links:
                line += link + ", "

            lines[i] = line.rstrip(", ")
            lines[i] += "\n"

        elif split[0] == "date":
            lines[i] = "date: " + \
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M') + '\n'

    if not note_text:
        with open(note.path, "w") as file:
            file.writelines(lines)


def load_registry(path):
    try:
        with open(path, 'rb') as file:
            return pickle.load(file)
    except Exception:
        return None


def save_registry(registry, path):
    with open(path, 'wb') as file:
        pickle.dump(registry, file)


class Registry:

    def __init__(self):
        self.notes = {}
        self.tags = {}

    def add_note(self, note, note_text=None):
        if not note_text:
            with open(note.path, 'r') as file:
                note_text = file.read()

        text_lines = note_text.splitlines()
        tags = set(split_list("tags", text_lines))
        for tag in tags:
            if tag not in self.tags:
                self.tags[tag] = set([])
            self.tags[tag].add(note.name)

        links = set(split_list("links", text_lines))
        for linked_note_name in links:
            if self.__is_note_valid(linked_note_name):
                other_note = self.notes[linked_note_name]
                self.__add_link(note, other_note)
                update_note_text(other_note)

        update_note_text(note, note_text=note_text)
        self.notes[note.name] = note

    def remove_note(self, note):
        self.notes.pop(note.name)

        empty_tags = []
        for tag in note.tags:
            self.tags[tag].remove(note.name)
            if self.tags[tag].empty():
                empty_tags.append(tag)
        for tag in empty_tags:
            self.tags.pop(tag)

        links = note.links.copy()
        for link in links:
            self.__remove_link(self.notes[link], note)
            update_note_text(self.notes[link])

    def remove_deleted_links_and_tags(self, note):
        if note.name in self.notes:
            old_note = self.notes.get(note.name)
            deleted_tags = old_note.tags - note.tags

            for deleted_tag in deleted_tags:
                self.tags[deleted_tag].remove(note.name)

            for deleted_tag in deleted_tags:
                if self.tags[deleted_tag].empty():
                    self.tags.pop(deleted_tag)
            deleted_links = old_note.links - note.links

            for deleted_link in deleted_links:
                if self.__is_note_valid(deleted_link):
                    linked_note = self.notes[deleted_link]
                    self.__remove_link(old_note, linked_note)
                    linked_note.update_text()

            update_note_text(note)

    def __clean(self):
        deleted_notes = []
        for note_name in self.notes:
            if not os.path.exists(self.notes[note_name].path):
                deleted_notes.append(self.notes[note_name])

        for note in deleted_notes:
            self.clean_up_note(note)

    def __add_link(self, first_note, second_note):
        first_note.links.add(second_note.name)
        second_note.links.add(first_note.name)

    def __remove_link(self, first_note, second_note):
        first_note.links.remove(second_note.name)
        second_note.links.remove(first_note.name)

    def __is_note_valid(self, note_name):
        return note_name in self.notes and os.path.exists(
            self.notes[note_name].path)


class NoteSaver(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        path = view.file_name()
        extension = os.path.splitext(path)[1]
        if extension == NOTE_EXTENSION:
            note_text = view.substr(sublime.Region(0, view.size()))
            registry = load_registry(REGISTRY_PATH)
            note = note_from_path(path)
            registry.add_note(note, note_text)
            registry.remove_deleted_links_and_tags(note)

            save_registry(registry, REGISTRY_PATH)

    def on_post_save(self, view):
        path = view.file_name()
        extension = os.path.splitext(path)[1]
        if extension == NOTE_EXTENSION:
            note = note_from_path(path)
            update_note_text(note)


class TagNoteInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, registry, tags):
        self.registry = registry
        self.tags = tags

    def list_items(self):
        if self.tags.empty():
            return []
        chosen_notes = self.registry.tags[self.tags[0]]
        for i in range(1, len(self.tags)):
            chosen_notes = chosen_notes & self.registry.tags[self.tags[i]]
        return list(chosen_notes)


class TagNotesInputHandler(sublime_plugin.TextInputHandler):
    def __init__(self, registry):
        self.registry = registry
        self.tags = []

    def confirm(self, text):
        self.tags = split_line(text)

    def next_input(self, args):
        return TagNoteInputHandler(self.registry, self.tags)


class LinkedNoteInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, command):
        self.command = command

    def list_items(self):
        v = self.command.view
        r = self.command.registry
        if v.file_name() is None:
            return []
        note_name = note_name_from_path(v.file_name())
        return list(r.notes[note_name].links)


class NoteNameInputHandler(sublime_plugin.ListInputHandler):
    def __init__(self, registry):
        self.registry = registry

    def list_items(self):
        return list(self.registry.notes.keys())


class ZamekPrintRegistryCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        registry = load_registry(REGISTRY_PATH)
        if registry:
            pprint.pprint(vars(registry))
        else:
            sublime.error_message(
                "Registry file doesn't exist. "
                "Use \"Zamek: Scan Directory For Notes\" to create it.")

        print(note_name_from_path(self.view.file_name()))


class ZamekOpenNoteCommand(sublime_plugin.TextCommand):
    def run(self, edit, note_name):
        if note_name:
            self.view.window().open_file(self.registry.notes[note_name].path)

    def input(self, args):
        self.registry = load_registry(REGISTRY_PATH)
        return NoteNameInputHandler(self.registry)


class ZamekOpenNoteWithTags(sublime_plugin.TextCommand):
    def run(self, edit, tag_notes, tag_note):
        self.view.window().open_file(self.registry.notes[tag_note].path)

    def input(self, args):
        self.registry = load_registry(REGISTRY_PATH)
        return TagNotesInputHandler(self.registry)


class ZamekOpenLinkedNote(sublime_plugin.TextCommand):
    def run(self, edit, linked_note):
        if linked_note:
            self.view.window().open_file(self.registry.notes[linked_note].path)

    def input(self, args):
        self.registry = load_registry(REGISTRY_PATH)
        return LinkedNoteInputHandler(self)


class ZamekDeleteNote(sublime_plugin.TextCommand):
    def run(self, edit):
        file_path = self.view.file_name()
        if file_path:
            (_, ext) = os.path.splitext(file_path)
            if ext == NOTE_EXTENSION:
                should_del = sublime.ok_cancel_dialog(
                    "Delete Zamek note? This will also delete the file from disk.", "Delete")
                if should_del:
                    registry = load_registry(REGISTRY_PATH)
                    if registry:
                        registry.remove_note(note_from_path(file_path))
                        os.remove(file_path)
                        save_registry(registry, REGISTRY_PATH)
            else:
                sublime.error_message("Not a Zamek note!")


class ZamekScanDirectoryForNotes(sublime_plugin.TextCommand):
    def run(self, edit, text):
        if text:
            path = os.path.abspath(text)
            if not os.path.exists(path) or not os.path.isdir(path):
                sublime.error_message("Invalid path: {}".format(text))
                return

            registry = load_registry(REGISTRY_PATH)
            if not registry:
                registry = Registry()

            note_paths = glob.glob(os.path.join(path, "**/*" + NOTE_EXTENSION))
            for note_path in note_paths:
                registry.add_note(note_from_path(note_path))

            save_registry(registry, REGISTRY_PATH)

    def input(self, args):
        return sublime_plugin.TextInputHandler()
