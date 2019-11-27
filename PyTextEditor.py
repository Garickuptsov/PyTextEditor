#!/usr/bin/pythton
# PyTextEditor v1.0

import sys
import os
import os.path
import tkinter as tk
from tkinter.filedialog import Open, SaveAs
from tkinter.messagebox import showinfo, showerror, askyesno
from tkinter.simpledialog import askstring, askinteger
from tkinter.colorchooser import askcolor

# General settinds
try:
    sys.path.append(os.getcwd())
    import TextConfig as tc
except:
    pass

START = '1.0'  # String, row
Font = 0  # Font

sel = tk.SEL
first_sel = sel + '.first'
last_sel = sel + '.last'


class Editor:

    startfiledir = '.'  # For dialogs
    editwindows = []  # To check for exit

    from TextConfig import (open_ask_user,
                            open_encoding,
                            save_use_know_encoding,
                            save_ask_user,
                            save_encoding)

    types = (('All files', '*'),
             ('Text file', '.txt'))

    colors = [{'fg': 'black', 'bg': 'white'},
              {'fg': 'white', 'bg': 'black'},
              {'fg': 'white', 'bg': 'red'}]

    fonts = [('courier', Font + 9, 'normal')]

    def __init__(self, load_first='', load_encode=''):
        if not isinstance(self, tk.Frame):
            raise TypeError('Edit must be inherited by tkinter.Frame')
        self.FileName = (None)
        self.last_find = None
        self.open_dialog = None
        self.save_dialog = None
        self.know_encoding = None
        self.currfile = None
        self.text.focus()
        if load_first:
            self.update()
            self.onOpen(load_first, load_encode)

    def start(self):
        self.menuBar = [('File', 0,
                         [('Open', 0, self.onOpen),
                          ('Save', 0, self.onSave),
                          ('Save As', 5, self.onSaveAs),
                          ('New', 0, self.onNew),
                          ('Quit', 0, self.onQuit)]),
                        ('Edit', 0,
                         [('Undo', 0, self.onUndo),
                          ('Redo', 0, self.onRedo),
                          ('Cut', 0, self.onCut),
                          ('Copy', 1, self.onCopy),
                          ('Paste', 0, self.onPaste),
                          ('Delete', 0, self.onDelete),
                          ('Select All', 0, self.onSelectAll)]),
                        ('Search', 0,
                         [('Goto', 0, self.onGoto),
                          ('Find', 0, self.onFind),
                          ('Refind', 0, self.onRefind),
                          ('Change', 0, self.onChange)]),
                        ('Tools', 0,
                         [('Pick Font', 6, self.onPickFont),
                          ('Font List', 0, self.onFontList),
                          ('Pick Bg', 3, self.onPickBg),
                          ('Pick Fg', 0, self.onPickFg),
                          ('Color list', 0, self.onColorList),
                          ('Info', 0, self.onInfo),
                          ('Clone', 1, self.onClone),
                          ('Bottom panel', 0, self.onPanel),
                          ('Hide bottom panel', 0, self.onHidePanel)])]
        self.ToolBar = [
            ('Save', self.onSave, {'side': tk.LEFT}),
            ('Cut', self.onCut, {'side': tk.LEFT}),
            ('Copy', self.onCopy, {'side': tk.LEFT}),
            ('Paste', self.onPaste, {'side': tk.LEFT}),
            ('Find', self.onFind, {'side': tk.RIGHT}),
            ('Quit', self.onQuit, {'side': tk.RIGHT})]

    def make_widges(self):
        """Make the widgets"""
        self.label = tk.Label(self, bg='black', fg='white')
        self.label.pack(side=tk.TOP, fill=tk.X)
        # Scrollbars
        scr_vertical = tk.Scrollbar(self)
        scr_horisontal = tk.Scrollbar(self, orient='horizontal')
        # Main text
        self.text = tk.Text(self, padx=5, wrap='none')
        
        self.text.config(undo=1, autoseparators=1)

        scr_horisontal.pack(side=tk.BOTTOM, fill=tk.X)
        scr_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.text.config(yscrollcommand=scr_vertical.set)
        self.text.config(xscrollcommand=scr_horisontal.set)
        scr_vertical.config(command=self.text.yview)
        scr_horisontal.config(command=self.text.xview)
        # Color adjustment
        startbg = tc.bg
        startfg = tc.fg
        startfont = tc.font
        self.text.config(font=startfont, bg=startbg, fg=startfg)

    # Menu operation of File

    def askopenfilename(self):
        """Objects remember directory/file last operation"""
        if not self.open_dialog:
            self.open_dialog = Open(initialdir=self.startfiledir,
                                    filetypes=self.types)
        return self.open_dialog.show()

    def my_ask_save_as_file_name(self):
        """Objects remember directorys/files last operation"""
        if not self.save_dialog:
            self.save_dialog = SaveAs(initialdir=self.startfiledir,
                                      filetypes=self.types)
        return self.save_dialog.show()

    def onOpen(self, load_first='', load_encode=''):
        """Open in text format with the encoding that was in argument"""
        # Change check
        if not askyesno('PyTextEditor', 'Text has changed: discard changes?'):
            return

        file = load_first or self.askopenfilename()
        if not file:
            return
        if not os.path.isfile(file):
            showerror('PyTextEditor', '{0} is not file!'.format(file))
            return
        # User selected encoding is used
        text = None
        if load_encode:
            try:
                text = open(file, 'r', encoding=load_encode).read()
                self.know_encoding = load_encode
            except (UnicodeError, LookupError, IOError):
                pass
        # If open_ask_user return True, then encoding is applied
        if text is None and self.open_ask_user:
            self.update()
            askuser = askstring('PyTextEditor',
                                'Enter encoding for open ',
                                initialvalue=self.open_encoding or
                                sys.getdefaultencoding() or '')
            if askuser:
                try:
                    text = open(file, 'r', encoding=askuser).read()
                    self.know_encoding = askuser
                except (UnicodeError, LookupError, IOError):
                    pass
        # If open_encoding not empty, then encoding is Latin-1
        if text is None and self.open_encoding:
            try:
                text = open(file, 'r', encoding=self.open_encoding).read()
                self.know_encoding = self.open_encoding
            except (UnicodeError, LookupError, IOError):
                pass
        # Trying use sys.getdefaultencoding()
        if text is None:
            try:
                text = open(file, 'r', encoding=sys.getdefaultencoding())
                text.read()
                self.know_encoding = sys.getdefaultencoding()
            except (UnicodeError, LookupError, IOError):
                pass
        # Use binary system
        if text is None:
            try:
                text = open(file, 'rb').read()
                text.replace(b'/r/n', b'/n')
                self.know_encoding = None
            except IOError:
                pass
        # If text is None return message with error
        if text is None:
            showerror('PyTextEditor', 'Could not decode and open file ' + file)
        else:
            self.set_file_name(file)
            self.set_all_text(text)
            self.text.edit_reset()
            self.text.edit_modified(0)  # Clear flag presence of changes

    def text_edit_modified(self):
        return self.text.edit_modified()

    def onSave(self):
        self.onSaveAs(self.currfile)

    def onSaveAs(self, force_file=None):
        """Save file in defind file"""
        # Use last encoding
        filename = force_file or self.my_ask_save_as_file_name()
        if not filename:
            return
        text = self.get_all_text()
        enpick = None

        if self.know_encoding and self.save_use_know_encoding >= 1 and force_file:
            try:
                text.encode(self.know_encoding)
                enpick = self.know_encoding
            except UnicodeError:
                pass
        # If save_ask_user is True, then apply
        # The encoding specified by the user
        if not enpick and self.save_ask_user:
            self.update()  # Or dialog can do not curl up
            askuser = askstring('PyTextEditor',
                                'Enter unicode for save',
                                initialvalue=(
                                    self.know_encoding or
                                    self.save_encoding or
                                    sys.getdefaultencoding() or
                                    ''))
            if askuser:
                try:
                    text.encode(askuser)
                    enpick = askuser
                except (UnicodeError, LookupError):
                    pass
        # Apply encoding from file
        if not enpick and self.save_encoding:
            try:
                text.encode(self.save_encoding)
                enpick = self.save_encoding
            except (UnicodeError, LookupError):
                pass
        # Use sys encoding
        if not enpick:
            try:
                text.encode(sys.getdefaultencoding())
                enpick = sys.getdefaultencoding()
            except (UnicodeError, LookupError):
                pass
        # Use encoding
        if not enpick:
            showerror('PyTextEditor',
                      'Could not encode for file ', filename)
        else:
            try:
                file = open(filename, 'w', encoding=enpick)
                file.write(text)
                file.close()
            except:
                showerror('PyTextEditor',
                          'Could not to write in file ', filename)
            else:
                self.file_name(filename)
                self.text.edit_modified(0)  # Clear flag presence of changes
                self.know_encoding = enpick

    def onNew(self):
        """starts editing a completely new file in the current window"""
        if self.text_edit_modified():
            if not askyesno('PyTextEditor',
                            'Text has changed: discard changed?'):
                return
        self.set_file_name(None)
        self.clear_all_text()  # Clear text
        self.text.edit_reset()  # Clear Undo/Redo
        self.text.edit_modified(0)  # Clear flag presence of changes
        self.know_encoding = None  # Encoding is None

    def onQuit(self):
        """Leaves the window"""
        assert False, 'onQuit must be defind in window-specific sublass'

    # Menu operation of Edit

    def onUndo(self):
        """Undoes the last edit action"""
        try:
            self.text.edit_undo()
        except:
            showerror('PyTextEditor', 'Nothing to undo')

    def onRedo(self):
        """Redo the last undone edit"""
        try:
            self.text.edit_redo()
        except:
            showerror('PyTextEditor', 'Nothing to redo')

    def onCopy(self):
        """get selected text save to system buffer"""
        # Return a list of ranges of text which have tag TAGNAME
        if not self.text.tag_ranges(sel):
            showerror('PyTextEditor', 'No text selected')
        else:
            text = self.text.get(first_sel, last_sel)

    def onPaste(self):
        """Paste text in insert place"""
        try:
            text = self.selection_get(selection='CLIPBOARD')
        except:
            showerror('PyTextEditor', 'Nothing to paste')
            return
        self.text.insert(tk.INSERT, text)  # Paste in current position
        self.text.tag_remove(sel, 0.0, tk.END)  # Remove
        self.text.tag_add(sel, tk.INSERT +
                          '-{0}{1}'.format(len(text), tk.INSERT))
        self.see(tk.INSERT)  # Show cursor

    def onDelete(self):
        """Delete selected text without save"""
        if not self.text.tag_ranges(sel):
            showerror('PyTextEditor', 'No text selected')
        else:
            self.text.delete(first_sel, last_sel)

    def onCut(self):
        """Copy and delete selected text"""
        if not self.text.tag_ranges(sel):
            showerror('PyTextEditor', 'No text selected')
        else:
            self.onCopy()
            self.onDelete()

    def onSelectAll(self):
        self.text.tag_add(sel, '0.0', tk.END + '-1c')  # Select all text
        self.text.mark_set(tk.INSERT, '0.0')  # Move position in start
        self.text.see(tk.INSERT)  # Show cursor

    # Menu operation of Search

    def onGoto(self, force_line=None):
        line = force_line or askinteger('PyTextEditor',
                                        'Enter line number')
        self.text.update()
        self.text.focus()
        if line is not None:
            max_index = self.text.index(tk.END + '-1c')
            max_line = int(max_index.split('.')[0])
            if line > 0 and line <= max_line:
                # Move in page
                self.text.mark_set(tk.INSERT, '{0}.0'.format(line))
                
                self.text.tag_remove(sel, '0.0', tk.END)

                self.text.tag_add(sel, tk.INSERT, 'insert + 1]')
                self.text.see(tk.INSERT)
            else:
                showerror('PyTextEditor', 'Bad line number')

    def onFind(self, last_key=None):
        key = last_key or askinteger('PyTextEditor',
                                     'Enter search string')
        self.text.update()
        self.text.focus()
        self.last_find = key
        if key:
            nocase = configs.get('caseinsens', True)
            # Searh key beginning from tk.INSERT until END
            where = self.text.search(key, tk.INSERT, tk.END, nocase=nocase)
            if where:
                # position past key
                past_key = where + '+{0}'.format(len(key))
                # Remove selection
                self.text.tag_remove(sel, 0.0, tk.END)
                # Select key
                self.text.tag_add(sel, where, past_key)
                # Move before paskey
                self.text.mark_set(tk.INSERT, paskey)
                self.text.see(paskey)
            else:
                showerror('PyTextEditor', 'String not found')

    def onRefind(self):
        self.onFind(self.last_find)

    def onChange(self):
        """Creature new window for change text"""
        child = tk.Toplevel(self)
        child.title('PyTextEditor')

        label = tk.Label(child, text='Find text:', width=15)
        label.grid(row=0, column=0)
        sec_label = tk.Label(child, text='Change to:', width=15)
        sec_label.grid(row=1, column=0)

        self.ent = tk.Entry(child)
        self.ent.grid(row=0, column=1)
        self.sec_ent = tk.Entry(child)
        self.sec_ent.grid(row=1, column=1)
        
        button = tk.Button(child, text='Find', command=(lambda: Find))
        button.grid(row=2, column=0)
        sec_button = tk.Button(child, text='Apply', command=(lambda: Apply))
        sec_button.grid(row=2, column=1)
        child.resizable(False, False)

        def Find():
            self.onFind(child.ent.get())

        def Apply():
            self.onDoChange(child.ent.get(), child.sec_ent.get())

    def onDoChange(self, find_text, change_to):
        """Chagne find_text to change_to"""
        if self.text.tag_ranges(sel):
            self.text.delete(first_sel, last_sel)
            self.text.insert(tk.INSERT, change_to)
            self.text.see(tk.INSERT)
            self.onFind(find_text)
            self.text.update()

    # Menu operation of Tools

    def onFontList(self):
        """Change font"""
        self.fonts.append(self.fonts[0])
        del self.fonts[0]
        self.text.config(font=self.fonts[0])

    def onPickBg(self):
        """Choise new bg"""
        self.pickColor('bg')

    def onPickFg(self):
        """Choise new fg"""
        self.pickColor('fg')

    def onPickFont(self):
        popup = tk.Toplevel(self)
        popup.title('PyTextEditor')
        popup.resizable(False, False)

        first_string_var = tk.StringVar()
        second_string_var = tk.StringVar()
        third_string_var = tk.StringVar()

        label = tk.Label(popup, text='Family')
        label.grid(row=0, column=0)
        ent = tk.Entry(popup, textvariable=first_string_var)
        ent.grid(row=0, column=1)

        second_label = tk.Label(popup, text='Size')
        second_label.grid(row=1, column=0)
        second_ent = tk.Entry(popup, textvariable=second_string_var)
        second_ent.grid(row=1, column=1)

        thrid_label = tk.Label(popup, text='Style')
        thrid_label.grid(row=2, column=0)
        thrid_ent = tk.Entry(popup, textvariable=third_string_var)
        thrid_ent.grid(row=2, column=1)

        first_string_var.set('courier')
        second_string_var.set('12')
        third_string_var.set('bold italic')

        button = tk.Button(popup,
                           text='Apply',
                           command=(lambda: self.onDoFont(first_string_var.get(),
                                                          second_string_var.get(),
                                                          third_string_var.get())))
        button.grid(row=3, column=0)

    def onDoFont(self, family, size, style):
        """Change font style, size, family"""
        try:
            self.text.config(font=(family, int(size), style))
        except:
            showerror('PyTextEditor', 'Bad font')

    def onColorList(self):
        """Change color"""
        self.colors.append(self.colors[0])
        del self.colors[0]
        self.text.config(fg=self.colors[0]['fg'], bg=self.colors[0]['bg'])

    def onInfo(self):
        """Dialogue with information"""
        text = self.get_all_text()
        text_bytes = len(text)
        lines = len(text.split('\n'))
        words = len(text.split())
        index = self.text.index(tk.INSERT)
        showinfo('PyTextEditor',
                 'Bytes: {0}\n'
                 'Lines: {1}\n'
                 'Words: {2}\n'
                 'Index: {3}\n'.format(text_bytes, lines, words, index))

    def onClone(self, make_window=True):
        """Open new edit window"""
        if not make_window:
            # New window
            new = None
        else:
            # The same process
            new = tk.Toplevel()
        myclass = self.__class__
        myclass(new)

    def pickColor(self, part):
        (triple, hexstr) = askcolor()
        if hexstr:
            self.text.config(**{part: hexstr})

    def onPanel(self):
        """Add the bottom panel"""
        if not self.istool_bar:
            self.make_tool_bar()

    def onHidePanel(self):
        """Hide the bottom panel"""
        if self.istool_bar:
            self.remove_tool_bar()

    # Other useful utilities

    def is_empty(self):
        return not self.get_all_text()

    def set_all_text(self, text):
        self.text.delete(0.0, tk.END)
        self.text.insert(0.0, text)
        self.text.mark_set(tk.INSERT, 0.0)  # move to start
        self.text.see(tk.INSERT)

    def clear_all_text(self):
        """Remove all text"""
        self.text.delete(0.0, tk.END)

    def get_all_text(self):
        """Return all text"""
        return self.text.get(0.0, tk.END)

    def file_name(self, name):
        """Creature file name"""
        self.currfile = name
        self.label.config(text=str(name))

    def get_file_name(self):
        """Return file name"""
        return self.currfile

    def set_file_name(self, rename):
        """Change file name"""
        self.currfile = rename
        self.label.config(text=str(rename))

    def set_know_encoding(self, encoding='utf-8'):
        """Change know encoding"""
        self.know_encoding = encoding

    def set_fg(self, color):
        """Set fg"""
        self.text.config(fg=color)

    def set_bg(self, color):
        """Set bg"""
        self.text.config(bg=color)

    def set_font(self, color):
        """Set font"""
        self.text.config(font=color)

    def set_height(self, lines):
        """Set lines"""
        self.text.config(height=lines)

    def set_width(self, chars):
        """Set width"""
        self.text.config(width=chars)

    def clear_modified(self):
        """Delete flag changes"""
        self.text.edit_modified(0)

    def is_modified(self):
        """Return flag changes"""
        return self.text.edit_modified()


class GuiMarker(tk.Frame):
    """Class for move witges"""
    menuBar = []
    ToolBar = []
    help_button = True
    istool_bar = False

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self.start()
        self.make_menu_bar()
        self.make_widges()

    def make_menu_bar(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        for (name, key, item) in self.menuBar:
            pulldown = tk.Menu(menu_bar)
            self.add_menu_items(pulldown, item)
            menu_bar.add_cascade(label=name, underline=key, menu=pulldown)
        if self.help_button:
            if sys.platform[:3] == 'win':
                # In windows
                menu_bar.add_command(label='Help', command=self.help)
            else:
                # In linux
                pulldown = tk.Menu(menu_bar)
                pulldown.add_command(label='About', command=self.help)
                menu_bar.add_cascade(label='Help', menu=pulldown)

    def remove_tool_bar(self):
        self.istool_bar = False
        self.tool_bar.destroy()

    def add_menu_items(self, menu, items):
        """Scan list of elements and add items"""
        for item in items:
            if type(item) == list:
                for num in item:
                    menu.entryconfig(num, state=tk.DISABLED)
            elif type(item[2]) != list:
                menu.add_command(label=item[0],
                                 underline=item[1],
                                 command=item[2])
            else:
                pullover = Menu(menu)
                self.add_menu_items(pullover, item[2])
                menu.add_cascade(label=item[0],
                                 underline=item[1],
                                 menu=pullover)

    def make_tool_bar(self):
        """Creature buttons at the bottom"""
        self.istool_bar = True
        if self.ToolBar:
            self.tool_bar = tk.Frame(self, relief=tk.SUNKEN, bd=2)
            self.tool_bar.pack(side=tk.BOTTOM, fill=tk.X)

            for (name, action, place) in self.ToolBar:
                tk.Button(self.tool_bar, text=name, command=action).pack(place)

    def make_widges(self):
        """Creature other witgets"""
        name = tk.Label(self,
                        width=40,
                        height=10,
                        relief=tk.SUNKEN,
                        text='self.__class__.__name__')
        name.pack(expand=tk.YES, fill=tk.BOTH, side=tk.TOP)

    def help(self):
        showinfo('PyTextEditor',
                 'Sorry, no help for ' + self.__class__.__name__)

    def start(self):
        pass


class TextEditor(Editor, GuiMarker):
    """Main menu which called quite"""

    def __init__(self, parent=None, load_first='', load_encode=''):
        GuiMarker.__init__(self, parent)
        Editor.__init__(self, load_first, load_encode)

        self.master.title('PyTextEditor')
        self.master.protocol('WM_DELETE_WINDOW', self.onQuit)
        Editor.editwindows.append(self)

    def onQuit(self):
        close = self.text_edit_modified()
        if close:
            close = askyesno('PyTextEditor',
                             'Text changed quite and discard changes?')
            if close is False:
                return
        if close:
            windows = Editor.editwindows
            changes = [window for window in windows
                       if window != self and self.text.edit_modified()]
            if not changes:
                GuiMarker.quit(self)
            else:
                if askyesno('PyTextEditor',
                            '{0} other edit window changed,'
                            ' quite?'.format(len(changes))):
                    GuiMarker.quit(self)
        else:
            GuiMarker.quit(self)


def main():
    """Main part"""
    try:
        fname = sys.argv[1]
    except:
        fname = None
    TextEditor(load_first=fname).pack(expand=tk.YES, fill=tk.BOTH)
    tk.mainloop()


if __name__ == '__main__':
    main()
