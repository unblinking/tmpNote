#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Joshua Gray
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


import wx
import wx.lib.agw.flatnotebook as fnb
import wx.stc as stc
import os
import datetime
import webbrowser
from tmpNoteIcon import gettmpNoteIconIcon


__author__ = 'Joshua Gray'
__email__ = 'joshua@tmpNote.com'
__copyright__ = 'Copyright tmpNote.com'
__license__ = 'GPL'
__version__ = '0.0.7'


# +-------------------------------------------------------------------------+
# | NEW CLASS: The Flat Notebook Creator                                    |
# | Always use the latest SVN version of AGW:                               |
# | http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/                  |
# +-------------------------------------------------------------------------+
class FlatNotebook(fnb.FlatNotebook):
    """Create a FlatNotebook."""

    def __init__(self, parent):
        """Define the initialization behavior of the FlatNotebook."""

        fnb.FlatNotebook.__init__(
                self,
                parent = parent,
                id = wx.ID_ANY,
                agwStyle = fnb.FNB_NO_TAB_FOCUS|fnb.FNB_X_ON_TAB
        )

        self.SetActiveTabColour((34,34,34))
        self.SetActiveTabTextColour((200,200,200))
        self.SetNonActiveTabTextColour((100,100,100))
        self.SetTabAreaColour((51,51,51))

        self.right_click_menu()
        self.custom_page()


    def right_click_menu(self):
        """Create a right-click menu for each FlatNotebook page tab."""

        menu = wx.Menu()
        self.SetRightClickMenu(menu)
        menu.Append(wx.ID_CLOSE, 'Close', 'Close')
        self.Bind(wx.EVT_MENU, self.close, id=wx.ID_CLOSE)


    def close(self, event):
        """Close the selected FlatNotebook page tab."""

        # Try deleting the currently selected notebook page.
        # This will trigger the EVT_FLATBOOK_PAGE_CLOSING event.
        # That event is bound to self.closing_file_event.
        self.DeletePage(self.GetSelection())


    def custom_page(self):
        """A page to display when all FlatNotebook page tabs are closed."""

        panel = wx.Panel(self)
        font = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        panel.SetFont(font)
        panel.SetBackgroundColour((34,34,34))
        panel.SetForegroundColour((255,255,255))
        # wx.StaticText(panel, -1, '\n\n\nSomething here later?')
        self.SetCustomPage(panel)



# +-------------------------------------------------------------------------+
# | NEW CLASS: Styled Text Control Creator                                  |
# +-------------------------------------------------------------------------+
class TxtCtrl(stc.StyledTextCtrl):
    """Create a StyledTextCtrl."""


    def __init__(self, parent, text, readonly):
        """Define the initialization behavior of the StyledTextCtrl."""

        stc.StyledTextCtrl.__init__(self, parent, wx.ID_ANY)
        self.SetTextRaw(text)
        self.SetReadOnly(readonly) # bool
        self.set_styles()


    def set_styles(self):
        """Put the style in StyledTextCtrl."""

        # Using generic wx.Font for cross platform compatibility
        font = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        self.StyleSetFont(stc.STC_STYLE_DEFAULT, font) 

        self.StyleSetForeground(stc.STC_STYLE_DEFAULT, (255,255,255))
        self.StyleSetBackground(stc.STC_STYLE_DEFAULT, (34,34,34))
        self.SetSelForeground(True, (255,255,255))
        self.SetSelBackground(True, (68,68,68))
        self.SetCaretForeground((0,255,0))
        self.SetUseTabs(0)
        self.SetTabWidth(4)

        # http://www.scintilla.org/ScintillaDoc.html#Margins
        self.SetMarginLeft(6) # Text area left margin.
        self.SetMarginWidth(0, 30) # Line numbers margin.
        self.SetMarginWidth(1, 0) # Non-folding symbols margin.
        self.SetMarginWidth(2, 0) # Folding symbols margin.

        # Reboot the styles after having just set the default styles.
        self.StyleClearAll()
        # After this we can set non-default styles.

        self.StyleSetForeground(wx.stc.STC_STYLE_LINENUMBER, (100,100,100))
        self.StyleSetBackground(wx.stc.STC_STYLE_LINENUMBER, (51,51,51))

        # Turn on word wrap by default.
        self.SetWrapMode(stc.STC_WRAP_WORD)



# +-------------------------------------------------------------------------+
# | NEW CLASS: TmpNote. Another text editor.                                |
# +-------------------------------------------------------------------------+
class TmpNote(wx.Frame): 
    """Create a TmpNote text editor application in a wx.Frame."""


    def __init__(self, parent):
        """Define the initialization behavior of the wx.Frame."""

        # Super is here for multiple inheritance in the future, not used yet.
        super(TmpNote, self).__init__(
                parent = parent,
                id = wx.ID_ANY,
                title = ' tmpNote ',
                size = (610, 400),
                style = wx.DEFAULT_FRAME_STYLE,
        )

        user_interface = self.ui()
        self.Show()


    def ui(self):
        """Assemble the pieces of the Graphical User Interface."""

        self.Bind(wx.EVT_CLOSE, self.destroyer_event)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.page_changed_event)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.closing_file_event)

        self.SetIcon(gettmpNoteIconIcon())

        self.menu_bar()
        self.status_bar()

        panel = wx.Panel(self)
        panel.SetBackgroundColour((34,34,34))

        # List to contain the FlatNotebook pages as they are created.
        # The objects in this list will be StyledTextCtrl objects.
        self.pages = []

        self.notebook = FlatNotebook(panel)
        first_page = self.new_file()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)

        panel.SetSizerAndFit(sizer)
        panel.Layout()


    def menu_bar(self):
        """Create a main menu bar."""

        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # Stock IDs:    http://wiki.wxpython.org/SpecialIDs
        # For menu items that do not use Stock IDs / Special IDs, use the
        # following ranges instead:
        # +-------------+-------------+-----------+
        # |  Menu name  | Range Start | Range End |
        # +-------------+-------------+-----------+
        # | File        |         100 |       199 |
        # | Edit        |         200 |       299 |
        # | Find        |         300 |       399 |
        # | View        |         400 |       499 |
        # | Preferences |         500 |       599 |
        # | Help        |         900 |       999 |
        # +-------------+-------------+-----------+

        # How to reserve these ID ranges so that something else doesn't use
        # one of these IDs before the menu does?

        # +-----------------------------------------------------------------+
        # | File menu.                                                      |
        # +-----------------------------------------------------------------+
        filemenu = wx.Menu()
        menubar.Append(filemenu, '&File')
        filemenu.Append(wx.ID_NEW, '&New File', 'Begin a new file.')
        self.Bind(wx.EVT_MENU, self.new_file_event, id=wx.ID_NEW)
        filemenu.Append(wx.ID_OPEN, '&Open File\tCtrl+O', 'Open an existing file.')
        self.Bind(wx.EVT_MENU, self.open_file_event, id=wx.ID_OPEN)
        filemenu.Append(wx.ID_SAVE, '&Save\tCtrl+S', 'Save using the current file name.')
        self.Bind(wx.EVT_MENU, self.save_file_event, id=wx.ID_SAVE)
        filemenu.Append(wx.ID_SAVEAS, 'Save &As', 'Save using a different file name.')
        self.Bind(wx.EVT_MENU, self.save_file_event, id=wx.ID_SAVEAS)
        filemenu.Append(wx.ID_CLOSE, '&Close File', 'Close the current file.')
        self.Bind(wx.EVT_MENU, self.close_file_event, id=wx.ID_CLOSE)
        filemenu.Append(wx.ID_CLOSE_ALL, 'Close All Files', 'Close all open files.')
        self.Bind(wx.EVT_MENU, self.close_all_event, id=wx.ID_CLOSE_ALL)
        # filemenu.AppendSeparator()
        # filemenu.Append(wx.ID_PRINT, '&Print', 'Print the current file.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_PRINT)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, 'E&xit', 'Exit the tmpNote application.')
        self.Bind(wx.EVT_MENU, self.destroyer_event, id=wx.ID_EXIT)

        # +-----------------------------------------------------------------+
        # | Edit menu.                                                      |
        # +-----------------------------------------------------------------+
        editmenu = wx.Menu()
        menubar.Append(editmenu, '&Edit')
        # editmenu.Append(wx.ID_UNDO, 'Undo', 'Undo an action.')
        # self.Bind(wx.EVT_MENU, self.undo_redo_event, id=wx.ID_UNDO)
        # editmenu.Append(wx.ID_REDO, 'Redo', 'Redo an action.')
        # self.Bind(wx.EVT_MENU, self.undo_redo_event, id=wx.ID_REDO)
        # editmenu.AppendSeparator()
        editmenu.Append(wx.ID_CUT, 'Cut\tCtrl+X', 'Cut selection from file.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del_sel_event, id=wx.ID_CUT)
        editmenu.Append(wx.ID_COPY, '&Copy\tCtrl+C', 'Copy selection from file.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del_sel_event, id=wx.ID_COPY)
        editmenu.Append(wx.ID_PASTE, '&Paste\tCtrl+V', 'Paste clipboard into file.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del_sel_event, id=wx.ID_PASTE)
        editmenu.Append(wx.ID_DELETE, 'Delete', 'Delete the selected text.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del_sel_event, id=wx.ID_DELETE)
        editmenu.AppendSeparator()
        editmenu.Append(wx.ID_SELECTALL, 'Select All', 'Select all text.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del_sel_event, id=wx.ID_SELECTALL)

        # +-----------------------------------------------------------------+
        # | Find menu.                                                      |
        # +-----------------------------------------------------------------+
        # findmenu = wx.Menu()
        # menubar.Append(findmenu, 'F&ind')
        # findmenu.Append(wx.ID_FIND, '&Find\tCtrl+f', 'Find a string.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_FIND)
        # findmenu.Append(301, 'Find &Next\tCtrl+g', 'Find the next occurance of a string.')
        # self.Bind(wx.EVT_MENU, None, id=301)
        # findmenu.Append(wx.ID_REPLACE, '&Replace\tCtrl+h', 'Replace a string.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_REPLACE)

        # +-----------------------------------------------------------------+
        # | View menu.                                                      |
        # +-----------------------------------------------------------------+
        self.viewmenu = wx.Menu()
        menubar.Append(self.viewmenu, '&View')
        self.word_wrap_option = self.viewmenu.Append(401, '&Word Wrap', 'Wrap lines at the text area width.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(401, True)
        self.Bind(wx.EVT_MENU, self.word_wrap_toggle_event, id=401)
        self.viewmenu.AppendSeparator()
        self.status_bar_option = self.viewmenu.Append(402, '&Status Bar', 'Display the status bar at the bottom of the window.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(402, True)
        self.Bind(wx.EVT_MENU, self.status_bar_toggle_event, id=402)
        self.notebook_visible_option = self.viewmenu.Append(406, 'Notebook', 'Display the notebook.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(406, True)
        self.Bind(wx.EVT_MENU, self.notebook_visible_toggle_event)
        self.viewmenu.AppendSeparator()
        self.line_numbers_option = self.viewmenu.Append(403, '&Line Numbers', 'Display line numbers in the left margin.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(403, True)
        self.Bind(wx.EVT_MENU, self.line_numbers_toggle_event, id=403)
        # self.folding_symbols_option = self.viewmenu.Append(404, 'Folding Symbols', 'Display folding symbols in the left margin.', kind=wx.ITEM_CHECK)
        # self.viewmenu.Check(404, True)
        # self.Bind(wx.EVT_MENU, None, id=404)
        # self.nonfolding_symbols_option = self.viewmenu.Append(405, 'Non-Folding Symbols', 'Display non-folding symbols in the left margin.', kind=wx.ITEM_CHECK)
        # self.viewmenu.Check(405, True)
        # self.Bind(wx.EVT_MENU, None, id=405)

        # +-----------------------------------------------------------------+
        # | Preferences menu.                                               |
        # +-----------------------------------------------------------------+
        # prefmenu = wx.Menu()
        # menubar.Append(prefmenu, 'Prefere&nces')

        # +-----------------------------------------------------------------+
        # | Help menu.                                                      |
        # +-----------------------------------------------------------------+
        helpmenu = wx.Menu()
        menubar.Append(helpmenu, '&Help')
        # helpmenu.Append(wx.ID_HELP, 'Helpful &Documentation', 'View the helpful documentation.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_HELP)
        # helpmenu.AppendSeparator()
        helpmenu.Append(wx.ID_ABOUT, '&About tmpNote', 'Learn about tmpNote')
        self.Bind(wx.EVT_MENU, self.about_event, id=wx.ID_ABOUT)
        self.about_already = False
        helpmenu.Append(901, 'tmpNote Website', 'Visit the tmpNote website.')
        self.Bind(wx.EVT_MENU, self.visit_website_event, id=901)


    def status_bar(self):
        """Create a status bar."""

        self.statusbar = self.CreateStatusBar()

        # Two sections of the status bar.
        # 0 | Updates and status messages.
        # 1 | Current open file name.
        self.statusbar.SetFieldsCount(2)
        # Ratio: 2 parts first section, 1 part second section, for size.
        self.statusbar.SetStatusWidths([-2, -1])

        self.statusbar.SetStatusText('Welcome to tmpNote.', 0)
        self.statusbar.SetStatusText('No open file.', 1)
        self.statusbar.Show()


    def status_bar_toggle_event(self, event):
        """Event asking to toggle the status bar visibility."""

        if event.GetId() == 402:
            self.status_bar_toggle_action()
        else:
            event.Skip()


    def status_bar_toggle_action(self):
        """Toggle the status bar visibility."""

        self.statusbar.Show(not self.statusbar.IsShown())
        self.SendSizeEvent()


    def notebook_visible_toggle_event(self, event):
        """Event asking to toggle the FlatNotebook visibility."""

        if event.GetId() == 406:
            self.notebook_visible_toggle_action()
        else:
            event.Skip()


    def notebook_visible_toggle_action(self):
        """Toggle the FlatNotebook visibility."""

        self.notebook.Show(not self.notebook.IsShown())
        self.viewmenu.Check(406, self.notebook.IsShown())
        self.SendSizeEvent()


    def line_numbers_toggle_event(self, event):
        """Event asking to toggle the line numbers margin visibility."""

        if event.GetId() == 403:
            self.line_numbers_toggle_action()
        else:
            event.Skip()


    def line_numbers_toggle_action(self):
        """Toggle the line numbers margin visibility."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        checkbox_orig_value = not self.viewmenu.IsChecked(403)
        page_count = self.notebook.GetPageCount()

        if page_count > 0:
            page = self.notebook.GetCurrentPage()
            if page.line_numbers == True:
                page.SetMarginWidth(0, 0)
                page.line_numbers = False
            else:
                page.SetMarginWidth(0, 30)
                page.line_numbers = True
        else:
            message = 'You selected to toggle line number visibility. There is no file open to toggle line number visibility.'
            caption = 'There is no file open to toggle line number visibility.'
            self.notify_ok(self, message, caption)
            self.viewmenu.Check(403, checkbox_orig_value)


    def word_wrap_toggle_event(self, event):
        """Event asking to toggle the word wrap option."""

        if event.GetId() == 401:
            self.word_wrap_toggle_action()
        else:
            event.Skip()


    def word_wrap_toggle_action(self):
        """Toggle the word wrap option."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        checkbox_orig_value = not self.viewmenu.IsChecked(401)
        page_count = self.notebook.GetPageCount()

        if page_count > 0:
            page = self.notebook.GetCurrentPage()
            page.SetWrapMode(not page.GetWrapMode())
            page.word_wrap = page.GetWrapMode()
        else:
            message = 'You selected to toggle word wrap. There is no file open to toggle word wrap. Please open a files before selecting to toggle word wrap.'
            caption = 'There is no file open to toggle word wrap.'
            self.notify_ok(self, message, caption)
            self.viewmenu.Check(401, checkbox_orig_value)


    def page_changed_event(self, event):
        """Event to gracefully change pages."""

        page = self.notebook.GetCurrentPage()

        self.statusbar.SetStatusText('You switched to ' + page.filename, 0)
        self.statusbar.SetStatusText(page.filename, 1)

        self.viewmenu.Check(401, page.word_wrap)
        self.viewmenu.Check(403, page.line_numbers)


    def new_file_event(self, event):
        """Event requesting to create a new file."""

        if event.GetId() == wx.ID_NEW:
            self.new_file()
        else:
            event.Skip()


    def new_file(self):
        """Create a new TextCtrl page and add it to the FlatNotebook."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        page = TxtCtrl(self, text='', readonly=False)
        self.pages.append(page)

        page.line_numbers = True
        page.word_wrap = True
        page.path = ''
        page.filename = 'Untitled'
        page.datetime = str(datetime.datetime.now())

        self.notebook.AddPage(
                page = page,
                text = 'Untitled',
                select = True,
        )


    def open_file_event(self, event):
        """Event requesting to open a file."""

        if event.GetId() == wx.ID_OPEN:
            self.open_file()
        else:
            event.Skip()


    def open_file(self):
        """Open the contents of a file into a new FlatNotebook page."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        dlg = wx.FileDialog(
                parent = self,
                message = 'Select a file to open.',
                defaultDir = os.getcwd(),
                defaultFile = 'tmpNote.txtmp',
                wildcard = 'All files (*.*)|*.*|tmpNote files (*.txtmp)|*.txtmp|Text files (*.txt)|*.txt',
                style = wx.OPEN|wx.CHANGE_DIR|wx.MULTIPLE
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result == wx.ID_OK:
            path = dlg.GetPath()
            filename_list = dlg.GetFilenames()
            for filename in filename_list:
                try:
                    f = open(path, 'r')
                    text = f.read()
                    f.close()

                    # Lose the default untitled page if that is the only
                    # page and there are no unsaved modifications to it,
                    # and then reset the pages list.
                    if (len(self.pages) == 1) and (self.pages[0].filename == 'Untitled') and (self.pages[0].GetModify() == False):
                        self.notebook.DeletePage(0)
                        self.pages = []

                    page = TxtCtrl(self, text=text, readonly=False)
                    self.pages.append(page)

                    page.line_numbers = True
                    page.word_wrap = True
                    page.path = path
                    page.filename = filename
                    page.datetime = str(datetime.datetime.now())

                    self.notebook.AddPage(
                            page = page,
                            text =  page.filename,
                            select = True,
                    )

                    page.SetSavePoint()

                    self.statusbar.SetStatusText('You opened ' + filename, 0)
                    self.statusbar.SetStatusText(filename, 1)
                except IOError, error:
                    error_dlg = wx.MessageDialog(
                            parent = self,
                            message = 'Error trying to open ' + filename + '.\n\n' + str(error),
                            caption = 'Error',
                            style = wx.ICON_EXCLAMATION
                    )
                    error_dlg.ShowModal()
                    error_dlg.Destroy()
                except UnicodeDecodeError, error:
                    error_dlg = wx.MessageDialog(
                            parent = self,
                            message = 'Error trying to open ' + filename + '.\n\n' + str(error),
                            caption = 'Error',
                            style = wx.ICON_EXCLAMATION
                    )
                    error_dlg.ShowModal()
                    error_dlg.Destroy()
                except:
                    error_dlg = wx.MessageDialog(
                            parent = self,
                            message = 'Error trying to open ' + filename + '.\n\n',
                            caption = 'Error',
                            style = wx.ICON_EXCLAMATION
                    )
                    error_dlg.ShowModal()
                    error_dlg.Destroy()
        else:
            self.statusbar.SetStatusText('The file was not opened.', 0)


    def save_file_event(self, event):
        """Event requesting to save a file, or save as."""

        page_count = self.notebook.GetPageCount()

        if (event.GetId() == wx.ID_SAVE or wx.ID_SAVEAS) and page_count == 0:
            self.statusbar.SetStatusText('There is no file open to save.', 0)
            message = 'You selected to save a file or to save as. There is no file open to save.'
            caption = 'There is no file open to save.'
            self.notify_ok(self, message, caption)
        elif event.GetId() == wx.ID_SAVE and page_count > 0:
            self.save_file()
        elif event.GetId() == wx.ID_SAVEAS  and page_count > 0:
            self.save_file_as()
        else:
            event.Skip()


    def save_file(self):
        """Save the selected page text to file."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        page = self.notebook.GetCurrentPage()

        if page.path == '':
            # Page hasn't been saved before, use save as instead.
            self.save_file_as()
        else:
            try:
                text = page.GetText()
                f = open(page.path, 'w')
                f.write(text)
                f.close()
                page.SetSavePoint()
                self.statusbar.SetStatusText('You saved ' + page.filename, 0)
                self.statusbar.SetStatusText(page.filename, 1)
            except IOError, error:
                error_dlg = wx.MessageDialog(
                        parent = self,
                        message = 'Error trying to save ' + page.filename + '.\n\n' + str(error),
                        caption = 'Error',
                        style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)
            except:
                error_dlg = wx.MessageDialog(
                        parent = self,
                        message = 'Error trying to save ' + page.filename + '.\n\n',
                        caption = 'Error',
                        style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)


    def save_file_as(self):
        """Save the selected page text to file, using Save As."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        page = self.notebook.GetCurrentPage()

        dlg = wx.FileDialog(
                parent = self,
                message = 'Select a file to save.',
                defaultDir = os.getcwd(),
                defaultFile = '',
                wildcard = 'All files (*.*)|*.*|tmpNote files (*.txtmp)|*.txtmp|Text files (*.txt)|*.txt',
                style = wx.SAVE|wx.OVERWRITE_PROMPT
        )
        result = dlg.ShowModal()
        path = dlg.GetPath()
        filename = dlg.GetFilename()
        dlg.Destroy()

        if result == wx.ID_OK:
            try:
                text = page.GetText()
                f = open(path, 'w')
                f.write(text)
                f.close()
                page.SetSavePoint()
                page.path = path
                page.filename = filename
                self.statusbar.SetStatusText('You saved ' + filename, 0)
                self.statusbar.SetStatusText(filename, 1)
                self.notebook.SetPageText(
                        page = self.notebook.GetSelection(),
                        text = filename
                )
            except IOError, error:
                error_dlg = wx.MessageDialog(
                        parent = self,
                        message = 'Error trying to save '+ page.filename + '.\n\n' + str(error),
                        caption = 'Error',
                        style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)
            except:
                error_dlg = wx.MessageDialog(
                        parent = self,
                        message = 'Error trying to save '+ page.filename + '.\n\n',
                        caption = 'Error',
                        style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)
        else:
            self.statusbar.SetStatusText('The file was not saved.', 0)


    def close_file_event(self, event):
        """Event requesting to close a file."""

        page_count = self.notebook.GetPageCount()

        if event.GetId() == wx.ID_CLOSE and page_count == 0:
            self.statusbar.SetStatusText('There is no file open to close.', 0)
            message = 'You selected to close a file. There is no file open to close.'
            caption = 'There is no file open to close.'
            self.notify_ok(self, message, caption)
        elif event.GetId() == wx.ID_CLOSE and page_count > 0:
            # Try deleting the currently selected notebook page.
            # This will trigger the EVT_FLATBOOK_PAGE_CLOSING event.
            # That event is bound to self.closing_file_event.
            self.notebook.DeletePage(self.notebook.GetSelection())
        else:
            event.Skip()


    def closing_file_event(self, event):
        """This event is triggered when any FlatNotebook page is deleted.

        When a FlatNotebook page is deleted we remove the associated page
        object (a TextCtrl) from the pages list.  At the same time we give the
        operator a chance to save modifications.
        """

        page = self.notebook.GetCurrentPage()
        filename = page.filename

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        if page.GetModify() == True:
            message = 'Discard unsaved modifications?'
            caption = 'Discard?'
            discard_page_ok = self.ask_yes_no(self, message, caption)
        else:
            discard_page_ok = True

        if discard_page_ok == True:
            self.pages.pop(self.pages.index(page))
            self.statusbar.SetStatusText(filename + ' was closed', 0)
        else:
            self.save_file()
            # After attempting to save we check for unsaved modifications again.
            # If they exist, it indicates that the save failed. Veto the event.
            if page.GetModify() == True:
                event.Veto()
                self.statusbar.SetStatusText(filename + ' was not closed.', 0)
            else:
                self.pages.pop(self.pages.index(page))
                self.statusbar.SetStatusText(filename + ' was closed.', 0)


    def close_all_event(self, event):
        """Event requesting to close all files."""

        page_count = self.notebook.GetPageCount()

        if event.GetId() == wx.ID_CLOSE_ALL and page_count == 0:
            self.statusbar.SetStatusText('There are no files open to close.', 0)
            message = 'You selected to close all files. There are no files open to close.'
            caption = 'There are no files open to close.'
            self.notify_ok(self, message, caption)
        elif event.GetId() == wx.ID_CLOSE_ALL and page_count > 0:
            self.close_all_action()
        else:
            event.Skip()


    def close_all_action(self):
        """Delete all FlatNotebook pages, gracefully, one page at a time."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        page_count = self.notebook.GetPageCount()
        ok_to_continue = True

        while page_count > 0:
            # Try deleting the currently selected notebook page.
            # This will trigger the EVT_FLATBOOK_PAGE_CLOSING event.
            # That event is bound to self.closing_file_event.
            self.notebook.DeletePage(self.notebook.GetSelection())
            if self.notebook.GetPageCount() < page_count:
                page_count = self.notebook.GetPageCount()
            else:
                ok_to_continue = False
                break
        return ok_to_continue


    def cut_copy_paste_del_sel_event(self, event):
        """Event requesting cut, copy, paste, delete, or select all text."""

        if event.GetId() == wx.ID_CUT or wx.ID_COPY or wx.ID_PASTE or wx.ID_DELETE or wx.ID_SELECTALL:
            self.cut_copy_paste_del_sel_action(event)
        else:
            event.Skip()


    def cut_copy_paste_del_sel_action(self, event):
        """Cut, copy, paste, delete, or select all text."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        text = self.FindFocus()
        if text is not None:
            if event.GetId() == wx.ID_CUT:
                text.Cut()
            elif event.GetId() == wx.ID_COPY:
                text.Copy()
            elif event.GetId() == wx.ID_PASTE:
                text.Paste()
            elif event.GetId() == wx.ID_DELETE:
                text.Clear()
            elif event.GetId() == wx.ID_SELECTALL:
                text.SelectAll()
        else:
            event.Skip()


#    def undo_redo_event(self, event):
#        """Undo and redo actions."""
#        # Take orders from the proper source events only.
#        if event.GetId() == wx.ID_UNDO:
#            event.Skip()
#        if event.GetId() == wx.ID_REDO:
#            event.Skip()
#        else:
#            event.Skip()


    def about_event(self, event):
        """Event requesting to display information about the application."""
        if event.GetId() == wx.ID_ABOUT:
            self.about()
        else:
            event.Skip()


    def about(self):
        """Display information about the tmpNote application in a page."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

        asciiart = (
                '  ________________________________________________\n' +
                '                          _     _                 \n' +
                '                          /|   /                  \n' +
                '  --_/_---_--_------__---/-| -/-----__--_/_----__-\n' +
                '    /    / /  )   /   ) /  | /    /   ) /    /___)\n' +
                '  _(_ __/_/__/___/___/_/___|/____(___/_(_ __(___ _\n' +
                '                /                                 \n' +
                '  tmpNote      /              Another text editor.\n\n\n\n'
        )
        info = (
                '  Version ' + __version__ + '\n' +
                '  License ' + __license__ + '\n' +
                '  ' + __copyright__
        )
        
        text = asciiart + info
        readonly = True
        page = TxtCtrl(self, text, readonly)
        self.pages.append(page)
        
        page.line_numbers = True
        page.word_wrap = True
        page.path = ''
        page.filename = 'About tmpNote'
        page.datetime = str(datetime.datetime.now())

        self.notebook.AddPage(
                page = page,
                text = 'About tmpNote',
                select = True,
        )

        page.SetSavePoint()


    def visit_website_event(self, event):
        """Visit the tmpNote website."""
        
        if event.GetId() == 901:
            webbrowser.open_new_tab('http://tmpNote.com/')
        else:
            event.Skip()


    def notify_ok(self, parent, message, caption):
        """Notify the operator about something."""
        
        dialog = wx.MessageDialog(
                parent = parent,
                message = message,
                caption = caption,
                style = wx.ICON_EXCLAMATION|wx.OK,
                pos = wx.DefaultPosition
        )
        result = dialog.ShowModal()
        dialog.Destroy()


    def ask_yes_no(self, parent, message, caption):
        """Ask the operator a yes/no question. Return True for yes, False for no."""
        
        dialog = wx.MessageDialog(
                parent = parent,
                message = message,
                caption = caption,
                style = wx.ICON_QUESTION|wx.YES_NO|wx.NO_DEFAULT,
                pos = wx.DefaultPosition
        )
        result = dialog.ShowModal()
        dialog.Destroy()
        
        if result == wx.ID_YES:
            return True
        else:
            return False


    def destroyer_event(self, event):
        """Event requesting to destroy the application."""

        if event.GetId() == wx.ID_EXIT or wx.EVT_CLOSE:
            self.destroyer_action()
        else:
            event.Skip()


    def destroyer_action(self):
        """Quit\Close\Destroy the application."""

        self.statusbar.SetStatusText('You are quitting the application.', 0)
        message = 'Are you sure you want to quit?'
        caption = 'Are you sure?'
        if self.ask_yes_no(self, message, caption) == True:
            self.statusbar.SetStatusText('You said yes to Quit.', 0)
            if self.close_all_action() == True:
                # Daisy, Daisy / Give me your answer, do.
                self.Destroy()
            else:
                self.statusbar.SetStatusText('Open files were not closed. Quit canceled', 0)
        else:
            self.statusbar.SetStatusText('Quit canceled.', 0)



# +-------------------------------------------------------------------------+
# | main.                                                                   |
# +-------------------------------------------------------------------------+
def main():
    app = wx.App(redirect=False)
    TmpNote(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
