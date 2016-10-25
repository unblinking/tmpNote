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
import keyword
import os
import datetime
import webbrowser
from tmpNoteIcon import gettmpNoteIconIcon

__author__ = 'Joshua Gray'
__email__ = 'joshua@tmpNote.com'
__copyright__ = 'Copyright tmpNote.com'
__license__ = 'GPL'
__version__ = '0.0.7'


# Always use the latest SVN version of AGW at http://svn.wxwidgets.org/svn/wx/wxPython/3rdParty/AGW/
class FlatNotebook(fnb.FlatNotebook):
    """Create a FlatNotebook."""

    def __init__(self, parent):
        """Define the initialization behavior of the FlatNotebook."""

        fnb.FlatNotebook.__init__(
            self,
            parent = parent,
            id = wx.ID_ANY,
            agwStyle = fnb.FNB_NO_TAB_FOCUS|fnb.FNB_X_ON_TAB|fnb.FNB_NAV_BUTTONS_WHEN_NEEDED|fnb.FNB_HIDE_ON_SINGLE_TAB|fnb.FNB_RIBBON_TABS
        )

        self.SetTabAreaColour((100,100,100))
        # Setting the active tab color was difficult for ribbon style tabs
        # FlatNotebook.py line 3817 was using LightColour(pc._tabAreaColour,60)
        # This gave a brighter version of the tab area color by a percentage of 60
        # I wanted to set active tab color independently
        # I changed it to pc._activeTabColour
        # Now I can use SetActiveTabColour() with the ribbon style tabs
        self.SetActiveTabColour((200,200,200))
        self.SetActiveTabTextColour((0,0,0))
        self.SetNonActiveTabTextColour((0,0,0))

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
        font = wx.Font(9, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        panel.SetFont(font)
        panel.SetBackgroundColour((34,34,34))
        panel.SetForegroundColour((255,255,255))
        # wx.StaticText(panel, -1, '\n\n\nSomething here later?')
        self.SetCustomPage(panel)


class TxtCtrl(stc.StyledTextCtrl):
    """Create a StyledTextCtrl."""

    def __init__(self, parent, text, readonly):
        """Define the initialization behavior of the StyledTextCtrl."""

        stc.StyledTextCtrl.__init__(self, parent, wx.ID_ANY)
        self.SetTextRaw(text)
        self.SetReadOnly(readonly) # bool
        self.Bind(stc.EVT_STC_MARGINCLICK, self.margin_click)

    # The following methods of margin_click, fold_all, and expand, are
    # copied from the demo. I haven't done anything special here.

    def margin_click(self, event):
        """Take proper action when a margin is clicked by the operator."""

        # Action for the folding symbols margin.
        if event.GetMargin() == 2:
            if event.GetShift() and event.GetControl():
                self.fold_all()
            else:
                lineClicked = self.LineFromPosition(event.GetPosition())
                if self.GetFoldLevel(lineClicked) and stc.STC_FOLDLEVELHEADERFLAG:
                    if event.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.expand(lineClicked, True, True, 1)
                    elif event.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)
        else:
            event.Skip()

    def fold_all(self):
        """Fold or unfold all folding symbols."""

        lineCount = self.GetLineCount()
        expanding = True
        # find out if folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) &\
                    stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break;
        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:
                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)
            lineNum = lineNum + 1

    def expand(self, line, doexpand, force=False, visLevels=0, level=-1):
        """Unfold folding symbols."""

        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doexpand:
                    self.ShowLines(line, line)
            if level == -1:
                level = self.GetFoldLevel(line)
            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.expand(line, doexpand, force, visLevels-1)
                else:
                    if doexpand and self.GetFoldExpanded(line):
                        line = self.expand(line, True, force, visLevels-1)
                    else:
                        line = self.expand(line, False, force, visLevels-1)
            else:
                line = line + 1;
        return line


class TmpNote(wx.Frame):
    """Use wx.Frame to create the graphical user interface."""

    def __init__(self, parent):
        """Define the initialization behavior of the wx.Frame."""

        # Super is here for multiple inheritance in the future, but not used yet.
        super(TmpNote, self).__init__(
            parent = parent,
            id = wx.ID_ANY,
            title = ' tmpNote ',
            size = (600, 400),
            style = wx.DEFAULT_FRAME_STYLE
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
        # Print was removed for now until I can find a way to print with cross platform compatibility
        # filemenu.AppendSeparator()
        # filemenu.Append(wx.ID_PRINT, '&Print', 'Print the current file.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_PRINT)
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, 'E&xit', 'Exit the tmpNote application.')
        self.Bind(wx.EVT_MENU, self.destroyer_event, id=wx.ID_EXIT)

        editmenu = wx.Menu()
        menubar.Append(editmenu, '&Edit')
        editmenu.Append(wx.ID_UNDO, 'Undo', 'Undo an action.')
        self.Bind(wx.EVT_MENU, self.undo_redo_event, id=wx.ID_UNDO)
        editmenu.Append(wx.ID_REDO, 'Redo', 'Redo an action.')
        self.Bind(wx.EVT_MENU, self.undo_redo_event, id=wx.ID_REDO)
        editmenu.AppendSeparator()
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

        # findmenu = wx.Menu()
        # menubar.Append(findmenu, 'F&ind')
        # findmenu.Append(wx.ID_FIND, '&Find\tCtrl+f', 'Find a string.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_FIND)
        # findmenu.Append(301, 'Find &Next\tCtrl+g', 'Find the next occurance of a string.')
        # self.Bind(wx.EVT_MENU, None, id=301)
        # findmenu.Append(wx.ID_REPLACE, '&Replace\tCtrl+h', 'Replace a string.')
        # self.Bind(wx.EVT_MENU, None, id=wx.ID_REPLACE)

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
        self.folding_symbols_option = self.viewmenu.Append(404, 'Folding Symbols', 'Display folding symbols in the left margin.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(404, False)
        self.Bind(wx.EVT_MENU, self.folding_symbols_toggle_event, id=404)
        # self.nonfolding_symbols_option = self.viewmenu.Append(405, 'Non-Folding Symbols', 'Display non-folding symbols in the left margin.', kind=wx.ITEM_CHECK)
        # self.viewmenu.Check(405, True)
        # self.Bind(wx.EVT_MENU, None, id=405)
        self.viewmenu.AppendSeparator()
        self.python_lexer_option = self.viewmenu.Append(407, 'Python syntax', 'Syntax highlighting using the Python lexer.', kind=wx.ITEM_CHECK)
        self.viewmenu.Check(407, False)
        self.Bind(wx.EVT_MENU, self.syntax_python_event, id=407)

        # prefmenu = wx.Menu()
        # menubar.Append(prefmenu, 'Prefere&nces')

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

    def set_styles_default(self):
        """Apply default styles to the current notebook page."""

        page = self.notebook.GetCurrentPage()

        # Set all style bytes to 0, remove all folding information.
        page.ClearDocumentStyle()
        # After this we can set base styles.

        page.SetUseTabs(False)
        page.SetUseAntiAliasing(True)
        page.SetTabWidth(4)
        page.SetViewWhiteSpace(False)
        page.SetViewEOL(False)
        # page.SetEOLMode(stc.STC_EOL_CRLF)

        # Using generic wx.Font for cross platform compatibility.
        font = wx.Font(9, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        page.StyleSetFont(stc.STC_STYLE_DEFAULT, font)

        page.StyleSetForeground(stc.STC_STYLE_DEFAULT, (255,255,255))
        page.StyleSetBackground(stc.STC_STYLE_DEFAULT, (34,34,34))
        page.SetSelForeground(True, (255,255,255))
        page.SetSelBackground(True, (68,68,68))
        page.SetCaretForeground((0,255,0))

        # Reboot the styles after having just set the base styles.
        page.StyleClearAll()
        # After this we can set non-base styles.

        page.StyleSetForeground(wx.stc.STC_STYLE_LINENUMBER, (151,151,151))
        page.StyleSetBackground(wx.stc.STC_STYLE_LINENUMBER, (51,51,51))

        # Use the NULL lexer for default styles.
        page.SetLexer(stc.STC_LEX_NULL)
        page.SetKeyWords(0, " ".join(keyword.kwlist))

        # For folding symbols: http://www.yellowbrain.com/stc/folding.html
        # Folding symbols margin settings.
        page.SetFoldMarginColour(True, (41,41,41)) # Color 1 of checker pattern
        page.SetFoldMarginHiColour(True, (51,51,51)) # Color 2 of checker pattern
        page.SetMarginSensitive(2, False)

    def set_styles_python(self):
        """Apply Python styles to the current notebook page."""

        page = self.notebook.GetCurrentPage()

        # Set all style bytes to 0, remove all folding information.
        page.ClearDocumentStyle()
        # After this we can set base styles.

        page.SetUseTabs(False)
        page.SetUseAntiAliasing(True)
        page.SetTabWidth(4)
        page.SetViewWhiteSpace(False)
        page.SetViewEOL(False)
        # page.SetEOLMode(stc.STC_EOL_CRLF)

        # Using generic wx.Font for cross platform compatibility.
        font = wx.Font(9, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        page.StyleSetFont(stc.STC_STYLE_DEFAULT, font)

        page.StyleSetForeground(stc.STC_STYLE_DEFAULT, (255,255,255))
        page.StyleSetBackground(stc.STC_STYLE_DEFAULT, (34,34,34))
        page.SetSelForeground(True, (255,255,255))
        page.SetSelBackground(True, (68,68,68))
        page.SetCaretForeground((0,255,0))

        # Reboot the styles after having just set the base styles.
        page.StyleClearAll()
        # After this we can set non-base styles.

        page.StyleSetForeground(wx.stc.STC_STYLE_LINENUMBER, (151,151,151))
        page.StyleSetBackground(wx.stc.STC_STYLE_LINENUMBER, (51,51,51))

        # Use the PYTHON lexer for Python styles.
        page.SetLexer(stc.STC_LEX_PYTHON)
        page.SetKeyWords(0, " ".join(keyword.kwlist))

        page.StyleSetSpec(stc.STC_P_COMMENTLINE, 'fore:#777777')
        page.StyleSetSpec(stc.STC_P_NUMBER, 'fore:#11ff11')
        page.StyleSetSpec(stc.STC_P_STRING, 'fore:#ff77ff')
        page.StyleSetSpec(stc.STC_P_CHARACTER, 'fore:#f777f7')
        page.StyleSetSpec(stc.STC_P_WORD, 'fore:#77ff77')
        page.StyleSetSpec(stc.STC_P_TRIPLE, 'fore:#ff7777')
        page.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'fore:#777777')
        page.StyleSetSpec(stc.STC_P_CLASSNAME, 'fore:#ffffff')
        page.StyleSetSpec(stc.STC_P_DEFNAME, 'fore:#7777ff')
        page.StyleSetSpec(stc.STC_P_OPERATOR, '')
        page.StyleSetSpec(stc.STC_P_IDENTIFIER, '')
        page.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'fore:#777777')

        # For folding symbols: http://www.yellowbrain.com/stc/folding.html
        # Define markers and colors for folding symbols.
        c1 = (51,51,51) # Color 1
        c2 = (151,151,151) # Color 2
        # These seven logical symbols make up the mask stc.STC_MASK_FOLDERS which we use a bit later.
        page.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, c1, c2)
        page.MarkerDefine(stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, c1, c2)
        page.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, c1, c2)
        page.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNERCURVE, c1, c2)
        page.MarkerDefine(stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, c1, c2)
        page.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, c1, c2)
        page.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE, c1, c2)
        # Folding symbols margin settings.
        page.SetFoldFlags(16) # 16 = Draw a solid line below folded markers
        page.SetFoldMarginColour(True, (41,41,41)) # Color 1 of checker pattern
        page.SetFoldMarginHiColour(True, (51,51,51)) # Color 2 of checker pattern
        page.SetProperty("fold", "1")
        page.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        page.SetMarginMask(2, stc.STC_MASK_FOLDERS) # Use the seven logical symbols defined a bit earlier.
        page.SetMarginSensitive(2, True)

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

    def show_notebook_if_not_shown(self):
        """Show the notebook if it is currently hidden."""

        if self.notebook.IsShown() == False:
            self.notebook_visible_toggle_action()

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

    def syntax_python_event(self, event):
        """Event asking to toggle syntax highlighting for Python."""

        if event.GetId() == 407:
            self.syntax_python_action()
        else:
            event.Skip()

    def syntax_python_action(self):
        """Toggle syntax highlighting with the Python lexer."""

        self.show_notebook_if_not_shown()

        checkbox_orig_value = not self.viewmenu.IsChecked(407)
        page = self.notebook.GetCurrentPage()
        page_count = self.notebook.GetPageCount()

        if page_count > 0:
            if self.viewmenu.IsChecked(407):
                self.set_styles_python()
                page.python_syntax = True
            else:
                self.set_styles_default()
                page.python_syntax = False
        else:
            message = 'You selected to toggle Python syntax highlighting. There is no file open to toggle syntax highlighting.'
            caption = 'There is no file open to toggle syntax highlighting.'
            self.notify_ok(self, message, caption)
            self.viewmenu.Check(407, checkbox_orig_value)

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

        self.show_notebook_if_not_shown()

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

    def folding_symbols_toggle_event(self, event):
        """Event asking to toggle the folding symbols margin visibility."""

        if event.GetId() == 404:
            self.folding_symbols_toggle_action()
        else:
            event.Skip()

    def folding_symbols_toggle_action(self):
        """Toggle the folding symbols margin visibility."""

        self.show_notebook_if_not_shown()

        checkbox_orig_value = not self.viewmenu.IsChecked(404)
        page_count = self.notebook.GetPageCount()

        if page_count > 0:
            page = self.notebook.GetCurrentPage()
            if page.folding_symbols == True:
                page.SetMarginWidth(2, 0)
                page.folding_symbols = False
            else:
                page.SetMarginWidth(2, 30)
                page.folding_symbols = True
        else:
            message = 'You selected to toggle folding symbols visibility. There is no file open to toggle folding symbols visibility.'
            caption = 'There is no file open to toggle folding symbols visibility.'
            self.notify_ok(self, message, caption)
            self.viewmenu.Check(404, checkbox_orig_value)

    def word_wrap_toggle_event(self, event):
        """Event asking to toggle the word wrap option."""

        if event.GetId() == 401:
            self.word_wrap_toggle_action()
        else:
            event.Skip()

    def word_wrap_toggle_action(self):
        """Toggle the word wrap option."""

        self.show_notebook_if_not_shown()

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

        self.statusbar.SetStatusText('You switched to {0}'.format(page.filename), 0)
        self.statusbar.SetStatusText(page.filename, 1)

        self.viewmenu.Check(401, page.word_wrap)
        self.viewmenu.Check(403, page.line_numbers)
        self.viewmenu.Check(404, page.folding_symbols)
        self.viewmenu.Check(407, page.python_syntax)

    def new_file_event(self, event):
        """Event requesting to create a new file."""

        if event.GetId() == wx.ID_NEW:
            self.new_file()
        else:
            event.Skip()

    def new_file(self):
        """Create a new TextCtrl page and add it to the FlatNotebook."""

        self.show_notebook_if_not_shown()

        page = TxtCtrl(self, text='', readonly=False)
        self.pages.append(page)

        page.SetUndoCollection(True)
        page.SetBufferedDraw(True)
        page.SetWrapMode(stc.STC_WRAP_WORD)

        page.python_syntax = False
        page.folding_symbols = False
        page.line_numbers = False
        page.word_wrap = True
        page.path = ''
        page.filename = 'Untitled'
        page.datetime = str(datetime.datetime.now())

        # http://www.scintilla.org/ScintillaDoc.html#Margins
        page.SetMarginLeft(6) # Text area left margin.
        page.SetMarginWidth(0, 0) # Line numbers margin.
        page.SetMarginWidth(1, 0) # Non-folding symbols margin.
        page.SetMarginWidth(2, 0) # Folding symbols margin.

        self.notebook.AddPage(
            page = page,
            text = 'Untitled',
            select = True
        )

        self.set_styles_default()
        page.SetFocus()

    def open_file_event(self, event):
        """Event requesting to open a file."""

        if event.GetId() == wx.ID_OPEN:
            self.open_file()
        else:
            event.Skip()

    def open_file(self):
        """Open the contents of a file into a new FlatNotebook page."""

        self.show_notebook_if_not_shown()

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
            paths = dlg.GetPaths()
            filenames = dlg.GetFilenames()
            for index, filename in enumerate(filenames):
                path = paths[index]
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

                    page.SetUndoCollection(True)
                    page.SetBufferedDraw(True)
                    page.SetWrapMode(stc.STC_WRAP_WORD)

                    page.python_syntax = False
                    page.folding_symbols = False
                    page.line_numbers = False
                    page.word_wrap = True
                    page.path = path
                    page.filename = filename
                    page.datetime = str(datetime.datetime.now())

                    # http://www.scintilla.org/ScintillaDoc.html#Margins
                    page.SetMarginLeft(6) # Text area left margin.
                    page.SetMarginWidth(0, 0) # Line numbers margin.
                    page.SetMarginWidth(1, 0) # Non-folding symbols margin.
                    page.SetMarginWidth(2, 0) # Folding symbols margin.

                    self.notebook.AddPage(
                        page = page,
                        text =  page.filename,
                        select = True
                    )

                    self.set_styles_default()
                    page.SetFocus()
                    page.SetSavePoint()

                    self.statusbar.SetStatusText('You opened {0}'.format(filename), 0)
                    self.statusbar.SetStatusText(filename, 1)
                except (IOError, UnicodeDecodeError) as error:
                    error_dlg = wx.MessageDialog(
                        parent = self,
                        message = 'Error trying to open {0}.\n\n{1}'.format(filename, error),
                        caption = 'Error',
                        style = wx.ICON_EXCLAMATION
                    )
                    error_dlg.ShowModal()
                    error_dlg.Destroy()
                except:
                    error_dlg = wx.MessageDialog(
                        parent = self,
                        message = 'Error trying to open {0}.\n\n'.format(filename),
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

        self.show_notebook_if_not_shown()

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
                self.statusbar.SetStatusText('You saved {0}'.format(page.filename), 0)
                self.statusbar.SetStatusText(page.filename, 1)
            except IOError, error:
                error_dlg = wx.MessageDialog(
                    parent = self,
                    message = 'Error trying to save {0}.\n\n{1}'.format(page.filename, error),
                    caption = 'Error',
                    style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)
            except:
                error_dlg = wx.MessageDialog(
                    parent = self,
                    message = 'Error trying to save {0}.\n\n'.format(page.filename),
                    caption = 'Error',
                    style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)

    def save_file_as(self):
        """Save the selected page text to file, using Save As."""

        self.show_notebook_if_not_shown()

        page = self.notebook.GetCurrentPage()

        if page.path == '':
            default_file = ''
        else:
            default_file = page.filename

        dlg = wx.FileDialog(
            parent = self,
            message = 'Select a file to save.',
            defaultDir = os.getcwd(),
            defaultFile = default_file,
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
                self.statusbar.SetStatusText('You saved {0}.'.format(filename), 0)
                self.statusbar.SetStatusText(filename, 1)
                self.notebook.SetPageText(
                        page = self.notebook.GetSelection(),
                        text = filename
                )
            except IOError, error:
                error_dlg = wx.MessageDialog(
                    parent = self,
                    message = 'Error trying to save {0}.\n\n{1},'.format(filename, error),
                    caption = 'Error',
                    style = wx.ICON_EXCLAMATION
                )
                error_dlg.ShowModal()
                error_dlg.Destroy()
                self.statusbar.SetStatusText('There was an error saving the file.', 0)
            except:
                error_dlg = wx.MessageDialog(
                    parent = self,
                    message = 'Error trying to save {0}.\n\n'.format(filename),
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

        self.show_notebook_if_not_shown()

        if page.GetModify() == True:
            message = 'Discard unsaved modifications?'
            caption = 'Discard?'
            discard_page_ok = self.ask_yes_no(self, message, caption)
        else:
            discard_page_ok = True

        if discard_page_ok == True:
            self.pages.pop(self.pages.index(page))
            self.statusbar.SetStatusText('{0} was closed.'.format(filename), 0)
            self.statusbar.SetStatusText('', 1)
        else:
            self.save_file_as()
            # After attempting to save we check for unsaved modifications again.
            # If they exist, it indicates that the save failed. Veto the event.
            if page.GetModify() == True:
                event.Veto()
                self.statusbar.SetStatusText('{0} was not closed.'.format(filename), 0)
            else:
                self.pages.pop(self.pages.index(page))
                self.statusbar.SetStatusText('{0} was closed.'.format(filename), 0)
                self.statusbar.SetStatusText('', 1)

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

        self.show_notebook_if_not_shown()

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

        self.show_notebook_if_not_shown()

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

    def undo_redo_event(self, event):
        """Event requesting to undo or redo action in the undo history."""
        if event.GetId() == wx.ID_UNDO or wx.ID_REDO:
            self.undo_redo_action(event)
        else:
            event.Skip()

    def undo_redo_action(self,event):
        """Undo or redo action or actions in the undo history."""

        page = self.notebook.GetCurrentPage()
        if event.GetId() == wx.ID_UNDO:
            page.Undo()
        elif event.GetId() == wx.ID_REDO:
            page.Redo()
        else:
            event.Skip()

    def about_event(self, event):
        """Event requesting to display information about the application."""
        if event.GetId() == wx.ID_ABOUT:
            self.about()
        else:
            event.Skip()

    def about(self):
        """Display information about the tmpNote application in a page."""

        self.show_notebook_if_not_shown()

        a1 = '  ________________________________________________'
        a2 = '                          _     _                 '
        a3 = '                          /|   /                  '
        a4 = '  --_/_---_--_------__---/-| -/-----__--_/_----__-'
        a5 = '    /    / /  )   /   ) /  | /    /   ) /    /___)'
        a6 = '  _(_ __/_/__/___/___/_/___|/____(___/_(_ __(___ _'
        a7 = '                /                                 '
        a8 = '  tmpNote      /              Another text editor.'

        asciiart = '{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n\n\n\n'.format(a1,a2,a3,a4,a5,a6,a7,a8)
        info = '  Version {0}\n  License {1}\n  {2}'.format(__version__, __license__, __copyright__)
        text = '{0}{1}'.format(asciiart, info)

        readonly = True
        page = TxtCtrl(self, text, readonly)
        self.pages.append(page)

        page.SetUndoCollection(False)
        page.SetBufferedDraw(True)
        page.SetWrapMode(stc.STC_WRAP_NONE)

        page.python_syntax = False
        page.folding_symbols = False
        page.line_numbers = False
        page.word_wrap = False
        page.path = ''
        page.filename = 'About tmpNote'
        page.datetime = str(datetime.datetime.now())

        # http://www.scintilla.org/ScintillaDoc.html#Margins
        page.SetMarginLeft(6) # Text area left margin.
        page.SetMarginWidth(0, 0) # Line numbers margin.
        page.SetMarginWidth(1, 0) # Non-folding symbols margin.
        page.SetMarginWidth(2, 0) # Folding symbols margin.

        self.notebook.AddPage(
            page = page,
            text = 'About tmpNote',
            select = True
        )

        self.set_styles_default()
        page.SetFocus()
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


def main():
    app = wx.App(redirect=True)
    TmpNote(None)
    app.MainLoop()

if __name__ == '__main__':
    main()
