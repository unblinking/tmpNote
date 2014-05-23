import wx
import wx.lib.agw.flatnotebook as fnb
import wx.stc as stc
import os
import datetime
import webbrowser
from tmpNoteIcon import gettmpNoteIconIcon, gettmpNoteIconBitmap
import tempfile, win32print, win32api

__author__ = 'Joshua Gray'
__email__ = 'joshua@tmpNote.com'
__copyright__ = 'Copyright 2014 tmpNote.com'
__license__ = 'GPL'
__version__ = '0.0.6'

'''
Copyright (C) 2014 Joshua Gray

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
BACKLOG
when opening files, open multiple at once.
Menu > Edit > Undo
Menu > Edit > Redo
Menu > Find > Find
Menu > Find > Find Next
Menu > Find > Replace
Menu > View > Folding Symbols
Menu > View > Non-Folding Symbols
Menu > Help > Helpful Documentation
'''

'''
DEFECTS
- Save/SaveAs/Wordwrap/LineNumbers when no file is open produces an error.
- About while notebook is hidden doesn't show the notebook.
- Hide status bar > hide notebook > show status bar > show notebook > now the word wrap horiz scroll bar is hidden behind the status bar.
'''



# +---------------------------------------------------------------------------+
# | NEW CLASS: Flat Notebook Creator                                          |
# +---------------------------------------------------------------------------+
class FlatNotebook(fnb.FlatNotebook):
    """Create a FlatNotebook."""


    def __init__(self, parent):

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
        """Create a right-click menu for each notebook page tab."""
        menu = wx.Menu()
        self.SetRightClickMenu(menu)
        menu.Append(wx.ID_CLOSE, 'Close File', 'Close File')
        self.Bind(wx.EVT_MENU, self.close, id=wx.ID_CLOSE)


    def close(self, event):
        """Close the selected notebook page tab and associated file."""
        # The page closing event will be caught and handled properly.
        self.DeletePage(self.GetSelection())


    def custom_page(self):
        """Page to display when all notebook pages are closed."""
        panel = wx.Panel(self)
        panel.SetFont(wx.Font(
            pointSize = 10,
            family = wx.SWISS,
            style = wx.NORMAL,
            weight = wx.NORMAL,
            faceName = u'Consolas',
            encoding=wx.FONTENCODING_DEFAULT
        ))
        panel.SetBackgroundColour((34,34,34))
        panel.SetForegroundColour((255,255,255))
        wx.StaticText(panel, -1, '\n\n\nTo start a new file, go to [ File > New File ] in the menu.\nTo open an existing file, go to [File > Open File ] in the menu.')
        wx.StaticBitmap(panel, -1, gettmpNoteIconBitmap())
        self.SetCustomPage(panel)



# +---------------------------------------------------------------------------+
# | NEW CLASS: Styled Text Control Creator                                    |
# +---------------------------------------------------------------------------+
class TxtCtrl(stc.StyledTextCtrl):
    """Create a StyledTextCtrl."""


    def __init__(self, parent, text, readonly):
        """Define the initialization behavior of the object."""

        stc.StyledTextCtrl.__init__(self, parent, wx.ID_ANY)
        self.SetTextRaw(text)
        self.SetReadOnly(readonly) # bool
        self.set_styles()


    def set_styles(self):
        """We put the style in StyledTextCtrl."""

        # Set the style attributes.
        self.StyleSetFontAttr(
                styleNum = stc.STC_STYLE_DEFAULT,
                size = 10,
                faceName = u'Consolas',
                bold = False,
                italic = False,
                underline = False
        )

        # Set the remaining default styles.
        self.StyleSetForeground(stc.STC_STYLE_DEFAULT, (255,255,255))
        self.StyleSetBackground(stc.STC_STYLE_DEFAULT, (34,34,34))
        self.SetSelForeground(True, (255,255,255))
        self.SetSelBackground(True, (68,68,68))
        self.SetCaretForeground((0,255,0))
        self.SetUseTabs(0)
        self.SetTabWidth(4)

        # Set the default margins.
        # http://www.scintilla.org/ScintillaDoc.html#Margins
        self.SetMarginLeft(6) # Text area left margin.
        self.SetMarginWidth(0, 30) # Line numbers margin.
        self.SetMarginWidth(1, 0) # Non-folding symbols margin.
        self.SetMarginWidth(2, 0) # Folding symbols margin.

        # Reboot the styles after having just set the default styles.
        self.StyleClearAll()

        # Set the line number styles.
        self.StyleSetForeground(wx.stc.STC_STYLE_LINENUMBER, (100,100,100))
        self.StyleSetBackground(wx.stc.STC_STYLE_LINENUMBER, (51,51,51))

        # Turn on word wrap by default.
        self.SetWrapMode(stc.STC_WRAP_WORD)



# +---------------------------------------------------------------------------+
# | NEW CLASS: The primary TmpNote application frame.                         |
# +---------------------------------------------------------------------------+
class TmpNote(wx.Frame): 
    """The primary tmpNote application frame."""


    def __init__(self, parent):

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
        """User interface."""

        # Bindings
        self.Bind(wx.EVT_CLOSE, self.destroyer)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.page_changed_event)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSING, self.closing_file_event)

        # Set the frame icon.
        self.SetIcon(gettmpNoteIconIcon())

        # Create the menu bar and status bar.
        self.menu_bar()
        self.status_bar()

        # Create a main panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour((34,34,34))

        # Empty list to contain each of the pages as they are created.
        # Pages in this list will be StylexTextCtrl objects.
        self.pages = []

        # Create the notebook and first new page.
        self.notebook = FlatNotebook(panel)
        first_page = self.new_file()

        # Create a sizer and add the notebook to it.
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)

        # Adjust the layout.
        panel.SetSizerAndFit(sizer)
        panel.Layout()


    def menu_bar(self):
        """Create the main menu."""

        menubar = wx.MenuBar()
        self.SetMenuBar(menubar)

        # +--------------------------------------------------------+
        # | For menu items that do not use Stock IDs / Special IDs |
        # |   ---   Stock IDs: http://wiki.wxpython.org/SpecialIDs |
        # | Use the following ranges instead.                      |
        # +--------------------------------------------------------+
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

        '''###########################################################################################################################################################
        How to reserve these ID ranges? So something else doesn't use one of them before I do?
        ###########################################################################################################################################################'''

        # +-------------------------------------------------------------------+
        # | File menu.                                                        |
        # +-------------------------------------------------------------------+
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
        self.Bind(wx.EVT_MENU, self.close_all, id=wx.ID_CLOSE_ALL)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_PRINT, '&Print', 'Print the current file.')
        self.Bind(wx.EVT_MENU, self.print_event, id=wx.ID_PRINT)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, 'E&xit', 'Exit the tmpNote application.')
        self.Bind(wx.EVT_MENU, self.destroyer, id=wx.ID_EXIT)

        # +-------------------------------------------------------------------+
        # | Edit menu.                                                        |
        # +-------------------------------------------------------------------+
        editmenu = wx.Menu()
        menubar.Append(editmenu, '&Edit')
        editmenu.Append(wx.ID_UNDO, 'Undo', 'Undo an action.')
        self.Bind(wx.EVT_MENU, self.undo_redo, id=wx.ID_UNDO)
        editmenu.Append(wx.ID_REDO, 'Redo', 'Redo an action.')
        self.Bind(wx.EVT_MENU, self.undo_redo, id=wx.ID_REDO)
        editmenu.AppendSeparator()
        editmenu.Append(wx.ID_CUT, 'Cut\tCtrl+X', 'Cut selection from file.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del, id=wx.ID_CUT)
        editmenu.Append(wx.ID_COPY, '&Copy\tCtrl+C', 'Copy selection from file.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del, id=wx.ID_COPY)
        editmenu.Append(wx.ID_PASTE, '&Paste\tCtrl+V', 'Paste clipboard into file.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del, id=wx.ID_PASTE)
        editmenu.Append(wx.ID_DELETE, 'Delete', 'Delete the selected text.')
        self.Bind(wx.EVT_MENU, self.cut_copy_paste_del, id=wx.ID_DELETE)
        editmenu.AppendSeparator()
        editmenu.Append(wx.ID_SELECTALL, 'Select All', 'Select all text.')
        self.Bind(wx.EVT_MENU, self.select_all, id=wx.ID_SELECTALL)

        # +-------------------------------------------------------------------+
        # | Find menu.                                                        |
        # +-------------------------------------------------------------------+
        findmenu = wx.Menu()
        menubar.Append(findmenu, 'F&ind')
        findmenu.Append(wx.ID_FIND, '&Find\tCtrl+f', 'Find a string.')
        self.Bind(wx.EVT_MENU, None, id=wx.ID_FIND)
        findmenu.Append(301, 'Find &Next\tCtrl+g', 'Find the next occurance of a string.')
        self.Bind(wx.EVT_MENU, None, id=301)
        findmenu.Append(wx.ID_REPLACE, '&Replace\tCtrl+h', 'Replace a string.')
        self.Bind(wx.EVT_MENU, None, id=wx.ID_REPLACE)

        # +-------------------------------------------------------------------+
        # | View menu.                                                        |
        # +-------------------------------------------------------------------+
        self.viewmenu = wx.Menu()
        menubar.Append(self.viewmenu, '&View')

        self.word_wrap_option = self.viewmenu.Append(401, '&Word Wrap', 'Wrap lines at the text area width.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(401, True)
        self.Bind(wx.EVT_MENU, self.word_wrap_toggle, id=401)

        self.viewmenu.AppendSeparator()

        self.status_bar_option = self.viewmenu.Append(402, '&Status Bar', 'Display the status bar at the bottom of the window.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(402, True)
        self.Bind(wx.EVT_MENU, self.status_bar_toggle, id=402)

        self.notebook_visible_option = self.viewmenu.Append(406, 'Notebook', 'Display the notebook.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(406, True)
        self.Bind(wx.EVT_MENU, self.notebook_visible_toggle)

        self.viewmenu.AppendSeparator()

        self.line_numbers_option = self.viewmenu.Append(403, '&Line Numbers', 'Display line numbers in the left margin.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(403, True)
        self.Bind(wx.EVT_MENU, self.line_numbers_toggle, id=403)

        self.folding_symbols_option = self.viewmenu.Append(404, 'Folding Symbols', 'Display folding symbols in the left margin.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(404, True)
        self.Bind(wx.EVT_MENU, None, id=404)

        self.nonfolding_symbols_option = self.viewmenu.Append(405, 'Non-Folding Symbols', 'Display non-folding symbols in the left margin.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(405, True)
        self.Bind(wx.EVT_MENU, None, id=405)

        # +-------------------------------------------------------------------+
        # | Preferences menu.                                                 |
        # +-------------------------------------------------------------------+
        prefmenu = wx.Menu()
        menubar.Append(prefmenu, 'Prefere&nces')

        # +-------------------------------------------------------------------+
        # | Help menu.                                                        |
        # +-------------------------------------------------------------------+
        helpmenu = wx.Menu()
        menubar.Append(helpmenu, '&Help')
        helpmenu.Append(wx.ID_HELP, 'Helpful &Documentation', 'View the helpful documentation.')
        self.Bind(wx.EVT_MENU, None, id=wx.ID_HELP)
        helpmenu.AppendSeparator()
        helpmenu.Append(wx.ID_ABOUT, '&About tmpNote', 'Learn about tmpNote')
        self.Bind(wx.EVT_MENU, self.about_event, id=wx.ID_ABOUT)
        self.about_already = False
        helpmenu.Append(901, 'tmpNote Website', 'Visit the tmpNote website.')
        self.Bind(wx.EVT_MENU, self.visit_website, id=901)


    def status_bar(self):
        """Create the status bar."""

        self.statusbar = self.CreateStatusBar()

        # +----------------------------------+
        # | Two sections of the status bar.  |
        # +---+------------------------------+
        # | 0 | Updates and status messages. |
        # +---+------------------------------+
        # | 1 | Current open file name.      |
        # +---+------------------------------+
        self.statusbar.SetFieldsCount(2)
        # Ratio: 2 parts first section, 1 part second section, for size.
        self.statusbar.SetStatusWidths([-2, -1])

        # Set the default text in all status bar fields.
        self.statusbar.SetStatusText('Welcome to tmpNote.', 0)
        self.statusbar.SetStatusText('No open file.', 1)

        self.statusbar.Show()


    def status_bar_toggle(self, event):
        """Toggle the status bar to show or hide."""

        # Take orders from the proper source events only.
        if event.GetId() == 402: # 402 = [ View > Status Bar ]
            self.statusbar.Show(not self.statusbar.IsShown())
            # Adjust the layout to accomodate the appearing/disappearing status bar.
            # self.Layout() # Commented: Not necessary in Windows 7 apparently, possibly other environments.
            self.SendSizeEvent()
            # self.Refresh() # Commented: Not necessary in Windows 7 apparently, possibly other environments.
        else:
            event.Skip()


    def notebook_visible_toggle(self, event):
        """Toggle the notebook to show or hide."""

        # Take orders from the proper source events only.
        if event.GetId() == 406: # 406 = [ View > Notebook ]
            self.notebook.Show(not self.notebook.IsShown())
        else:
            event.Skip()


    def line_numbers_toggle(self, event):
        """Toggle the line numbers margin to show or hide."""
        # Take orders from the proper source events only.
        if event.GetId() == 403: # 403 = [ Menu > View > Line Numbers ]
            page = self.notebook.GetCurrentPage()
            if page.line_numbers == True:
                # Narrow the margin and set flag to False.
                page.SetMarginWidth(0, 0) # Width 0 pixels.
                page.line_numbers = False
            else:
                # Widen the margin and set flag to True.
                page.SetMarginWidth(0, 30) # Width 30 pixels.
                page.line_numbers = True
        else:
            event.Skip()


    def word_wrap_toggle(self, event):
        """Toggle the word wrap format on or off."""
        # Take orders from the proper source events only.
        if event.GetId() == 401: # 401 = [ Menu > View > Word Wrap ]
            page = self.notebook.GetCurrentPage()
            if page.word_wrap == True:
                # Turn off word wrap.
                page.SetWrapMode(stc.STC_WRAP_NONE)
                page.word_wrap = False
            else:
                # Turn on word wrap.
                page.SetWrapMode(stc.STC_WRAP_WORD)
                page.word_wrap = True
        else:
            event.Skip()


    def page_changed_event(self, event):
        page = self.notebook.GetCurrentPage()

        # Fix the status bar fields.
        self.statusbar.SetStatusText('You switched to ' + page.filename, 0)
        self.statusbar.SetStatusText(page.filename, 1)

        # Fix the view menu item settings to match the page.
        # Toggle word wrap menu item
        if page.word_wrap == True:
            # Set the toggle word wrap menu item to be checked.
            self.viewmenu.Check(401, True)
        else:
            # Set the toggle word wrap menu item to be unchecked.
            self.viewmenu.Check(401, False)
        # Toggle line numbers menu item
        if page.line_numbers == True:
            # Set the toggle line numbers menu item to be checked.
            self.viewmenu.Check(403, True)
        else:
            # Set the toggle line numbers menu item to be unchecked.
            self.viewmenu.Check(403, False)


    def new_file_event(self, event):
        """Start a new file."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_NEW:
            self.new_file()
        else:
            event.Skip()


    def new_file(self):
        """Create a new FlatNotebook Page/Tab/File."""

        # Create a new page object in the pages list.
        page = TxtCtrl(self, text='', readonly=False)
        self.pages.append(page)

        # Set the new page object's properties
        page.line_numbers = True
        page.word_wrap = True
        page.path = ''
        page.filename = 'Untitled'
        page.datetime = str(datetime.datetime.now())

        # Add the page to the notebook.
        self.notebook.AddPage(
                page = page,
                text = 'Untitled',
                select = True,
        )


    def open_file_event(self, event):
        """Open a file, the event."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_OPEN:
            self.open_file()
        else:
            event.Skip()


    def open_file(self):
        """Open a file."""

        dlg = wx.FileDialog(
                parent = self,
                message = 'Select a file to open.',
                defaultDir = os.getcwd(),
                defaultFile = 'tmpNote.txtmp',
                wildcard = 'All files (*.*)|*.*|tmpNote files (*.txtmp)|*.txtmp|Text files (*.txt)|*.txt',
                style = wx.OPEN|wx.CHANGE_DIR
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        
        # Operator selects a file and clicks OK.
        if result == wx.ID_OK:
            path = dlg.GetPath()
            filename = dlg.GetFilename()
            try:
                # Open the file, read its contents, and then close it.
                f = open(path, 'r')
                text = f.read()
                f.close()

                # Close the default untitled page if that was the only thing open and it wasn't edited.
                if (len(self.pages) == 1) and (self.pages[0].filename == 'Untitled') and (self.pages[0].GetModify() == False):
                    # Remove the untitled page from the notebook.
                    self.notebook.DeletePage(0)
                    # Reset the pages list.
                    self.pages = []

                # Create a new page object in the pages list.
                page = TxtCtrl(self, text=text, readonly=False)
                self.pages.append(page)

                # Set the new page object's properties
                page.line_numbers = True
                page.word_wrap = True
                page.path = path
                page.filename = filename
                page.datetime = str(datetime.datetime.now())

                # Add the page to the notebook.
                self.notebook.AddPage(
                        page = page,
                        text =  page.filename,
                        select = True,
                )

                # No changes to be saved yet.
                page.SetSavePoint()

                # Update the status bar fields.
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
        # Operator clicks Cancel.
        else:
            self.statusbar.SetStatusText('You clicked cancel.  The file was not opened.', 0)


    def save_file_event(self, event):
        """Save a file, or save a file as."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_SAVE:
            self.save_file()
        elif event.GetId() == wx.ID_SAVEAS:
            self.save_file_as()
        else:
            event.Skip()


    def save_file(self):
        """Save a file."""

        page = self.notebook.GetCurrentPage()
        if page.path == '':
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
        """Save a file, as."""
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

        # Operator selects a file and clicks OK.
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
                # Fix the notebook page label/tab text
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

        # Operator clicks Cancel.
        else:
            self.statusbar.SetStatusText('You clicked cancel.  The file was not saved.', 0)


    def close_file_event(self, event):
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_CLOSE:
            # Just try closing the currently selected notebook page immediately.
            # This action will trigger the EVT_FLATBOOK_PAGE_CLOSING event.
            # That event is bound to self.closing_file_event.
            self.notebook.DeletePage(self.notebook.GetSelection())
        else:
            event.Skip()


    def closing_file_event(self, event):
        """Deal with a closing file."""
        page = self.notebook.GetCurrentPage()
        filename = page.filename
        # What if page modifications haven't been saved yet?
        modified = page.GetModify()
        if modified == True:
            # Ask permission to discard changes.
            discard = self.ask_discard_changes()
        else:
            # No unsaved modifications
            discard = True
        # If changes were saved or can be discarded.
        if discard == True:
            # Do nothing to stop the closing.
            # Remove the page from the pages list.
            self.pages.pop(self.pages.index(page))
            # Update the status bar fields.
            self.statusbar.SetStatusText(filename + ' was closed', 0)
        # If changes were not saved and cannot be discarded.
        else:
            # Save the changes.
            self.save_file()
            # Did the save fail? To find out, lets see if there still unsaved modifications.
            save_file_failed = page.GetModify()
            # If the save failed, do not close, otherwise keep going.
            if save_file_failed == True:
                # Veto the closing page event.
                event.Veto()
                self.statusbar.SetStatusText(filename + ' was not closed.', 0)
            else:
                # Remove the page from the pages list.
                self.pages.pop(self.pages.index(page))
                # Update the status bar fields.
                self.statusbar.SetStatusText(filename + ' was closed', 0)


    def close_all(self, event):
        """Close all open files."""
        
        # Close any open notebook pages.
        # First, how many pages do we start with?
        page_count = self.notebook.GetPageCount()
        # So far, we are OK to continue with close_all.
        ok_to_continue = True
        # If any pages are still open, try closing them one by one.
        # This is similar to the close_file_event, except for all files.
        while page_count > 0:
            # Just try closing the currently selected notebook page immediately.
            # This action will trigger the EVT_FLATBOOK_PAGE_CLOSING event.
            # That event is bound to self.closing_file_event.
            self.notebook.DeletePage(self.notebook.GetSelection())
            # How many pages are left open now?
            new_page_count = self.notebook.GetPageCount()
            # Did the page count go down as expected?
            if new_page_count < page_count:
                # If so, set the page_count to the new number of pages.
                page_count = self.notebook.GetPageCount()
            else:
                # If not, something stopped the page from closing, do not continue with close_all.
                ok_to_continue = False
                break
        return ok_to_continue


    def ask_discard_changes(self):
        """Ask the operator if they want to proceed without saving first (discard changes)."""

        dlg = wx.MessageDialog(
                parent = self,
                message = "Discard unsaved changes?",
                caption = "Discard unsaved changes?",
                style = wx.ICON_QUESTION|wx.YES_NO|wx.NO_DEFAULT,
        )
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_YES:
            return True
        else:
            return False


    def cut_copy_paste_del(self, event):
        """Cut, copy, paste, or delete text."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_CUT:
            text = self.FindFocus()
            if text is not None:
                text.Cut()
        if event.GetId() == wx.ID_COPY:
            text = self.FindFocus()
            if text is not None:
                text.Copy()
        if event.GetId() == wx.ID_PASTE:
            text = self.FindFocus()
            if text is not None:
                text.Paste()
        if event.GetId() == wx.ID_DELETE:
            text = self.FindFocus()
            if text is not None:
                text.Clear()
        else:
            event.Skip()


    def undo_redo(self, event):
        """Undo and redo actions."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_UNDO:
            return None
        if event.GetId() == wx.ID_REDO:
            return None
        else:
            event.Skip()


    def select_all(self, event):
        """Select all text."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_SELECTALL:
            text = self.FindFocus()
            if text is not None:
                text.SelectAll()
        else:
            event.Skip()


    def print_event(self, event):
        """Print the page text."""
        # http://timgolden.me.uk/python/win32_how_do_i/print.html
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_PRINT:
            page = self.notebook.GetCurrentPage()
            text = page.GetText()
            filename = tempfile.mktemp (".txt")
            open (filename, "w").write (text)
            win32api.ShellExecute (
                0,
                "print",
                filename,
                '/d:"%s"' % win32print.GetDefaultPrinter (),
                ".",
                0
            )
        else:
            event.Skip()


    def about_event(self, event):
        """Start a new file."""
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_ABOUT:
            self.about()
        else:
            event.Skip()


    def about(self):
        """Request to view information about the application."""

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
        
        # Set a few page properties
        page.line_numbers = True
        page.word_wrap = True
        page.path = ''
        page.filename = 'About tmpNote'
        page.datetime = str(datetime.datetime.now())

        # Display the about information in a new notebook page.
        self.notebook.AddPage(
                page = page,
                text = 'About tmpNote',
                select = True,
        )

        page.SetSavePoint()


    def visit_website(self, event):
        """Visit the tmpNote website."""
        
        # Take orders from the proper source events only.
        if event.GetId() == 901: # 901 = [ Menu > Help > Visit Website ]
            webbrowser.open_new_tab('http://www.tmpNote.com/')
        else:
            event.Skip()


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


    def destroyer(self, event):
        """Quit\Close\Destroy the application."""
        
        # Take orders from the proper source events only.
        if event.GetId() == wx.ID_EXIT or wx.EVT_CLOSE:
            message = 'Are you sure you want to quit?'
            caption = 'Are you sure?'
            if self.ask_yes_no(self, message, caption) == True:
                # Help close all open files gracefully
                # Also, give a chance to cancel if unsaved changes exist.
                if self.close_all(self) == True:
                    # Daisy, Daisy / Give me your answer, do.
                    self.Destroy()
        # Else not the proper source events.
        else:
            event.Skip()



# +---------------------------------------------------------------------------+
# | main.                                                                     |
# +---------------------------------------------------------------------------+
def main():
    app = wx.App(redirect=True)
    TmpNote(None)
    app.MainLoop()

if __name__ == '__main__':
    main()


