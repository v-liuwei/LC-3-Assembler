import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from assemble import assemble, open_file, save_result
import time
import os


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.geometry('600x650')
        self.maintitle = 'LC-3 Assembler'
        self.font = ('Courier New', 10)
        self.file_saved = True
        self.create_widgets()
        self.new()
        self.always_run()

    def create_widgets(self):
        self.create_frame()
        self.create_textbox()
        self.create_button()
        self.create_hotkey()
        self.create_footer()
        self.create_menu()

    def create_frame(self):
        self.header = tk.Frame(self)
        self.main = tk.Frame(self)
        self.footer = tk.Frame(self)
        self.header.pack(side='top', fill='both')
        self.footer.pack(side='bottom', fill='both')
        self.main.pack(side='top', fill='both')
        self.inputframe = tk.LabelFrame(self.main, text='Editor')
        self.outputframe = tk.LabelFrame(self.main, text='Output')
        self.infoframe = tk.LabelFrame(self.main, text='Info')
        self.inputframe.grid(row=0, column=0, rowspan=2, columnspan=3, sticky='nswe')
        self.outputframe.grid(row=0, column=3, rowspan=2, columnspan=1, sticky='nswe')
        self.infoframe.grid(row=2, column=0, rowspan=1, columnspan=4, sticky='nswe')
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=1)
        self.main.grid_columnconfigure(2, weight=1)
        self.main.grid_columnconfigure(3, weight=6)
        self.main.grid_rowconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_rowconfigure(2, weight=19)

    def create_textbox(self):
        # create input box
        self.inputx = tk.Scrollbar(self.inputframe, orient='horizontal')
        self.inputy = tk.Scrollbar(self.inputframe)
        self.inputx.pack(side='bottom', fill='x')
        self.inputy.pack(side='right', fill='y')
        self.inputbox = tk.Text(self.inputframe, font=self.font, undo=True, wrap='none',
                                xscrollcommand=self.inputx.set, yscrollcommand=self.inputy.set)
        self.inputbox.pack(fill='both')
        self.inputx.config(command=self.inputbox.xview)
        self.inputy.config(command=self.inputbox.yview)

        # create output box
        self.outputx = tk.Scrollbar(self.outputframe, orient='horizontal')
        self.outputy = tk.Scrollbar(self.outputframe)
        self.outputx.pack(side='bottom', fill='x')
        self.outputy.pack(side='right', fill='y')
        self.outputbox = tk.Text(self.outputframe, font=self.font,
                                 xscrollcommand=self.outputx.set, yscrollcommand=self.outputy.set)
        self.outputbox.pack(fill='both')
        self.outputbox.config(state=tk.DISABLED)
        self.outputx.config(command=self.outputbox.xview)
        self.outputy.config(command=self.outputbox.yview)

        # create info box
        self.infox = tk.Scrollbar(self.infoframe, orient='horizontal', bd=1)
        self.infoy = tk.Scrollbar(self.infoframe, bd=1)
        self.infox.pack(side='bottom', fill='x')
        self.infoy.pack(side='right', fill='y')
        self.infobox = tk.Text(self.infoframe, font=self.font,
                               xscrollcommand=self.infox.set, yscrollcommand=self.infoy.set)
        self.infobox.pack(fill='both')
        self.infox.config(command=self.infobox.xview)
        self.infoy.config(command=self.infobox.yview)
        self.infobox.config(state=tk.DISABLED)

    def create_button(self):
        self.new_btn = tk.Button(self.header, text='New', height=1, width=8,
                                 font=self.font, command=self.new)
        self.new_btn.pack(side='left')
        self.open_btn = tk.Button(self.header, text='Open', height=1, width=8,
                                  font=self.font, command=self.open)
        self.open_btn.pack(side='left')
        self.save_btn = tk.Button(self.header, text='Save', height=1, width=8,
                                  font=self.font, command=self.save)
        self.save_btn.pack(side='left')
        # self.save_as_btn = tk.Button(self.header, text='Save As', height=1, width=8,
        #                              font=self.font, command=self.save_as)
        # self.save_as_btn.pack(side='left')
        self.assemble_btn = tk.Button(self.header, text='Assemble', height=1, width=8,
                                      font=self.font, command=self.assemble)
        self.assemble_btn.pack(side='left')

    def create_footer(self):
        self.footinfo = tk.Label(self.footer, text='Powered by peer pressure',
                                 relief='groove')
        self.footinfo.pack(side='left', padx=2, pady=2)
        self.line = tk.StringVar()
        self.line_label = tk.Label(self.footer, textvariable=self.line, font=self.font,
                                   relief='sunken', height=1, width=10)
        self.line_label.pack(side='right', padx=2)
        self.line.set('Line 1')

    def create_menu(self):
        self.menu = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label='New            Ctrl+N', underline=0, command=self.new)
        self.file_menu.add_command(label='Open...        Ctrl+O', command=self.open)
        self.file_menu.add_command(label='Save            Ctrl+S', command=self.save)
        self.file_menu.add_command(label='Save As...', command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', command=self.quit)
        self.menu.add_cascade(label='File', underline=1, menu=self.file_menu)
        self.edit_menu = tk.Menu(self.menu, tearoff=False)
        self.edit_menu.add_command(label='Undo        Ctrl+Z', command=self.inputbox.edit_undo)
        self.edit_menu.add_command(label='Redo        Ctrl+Y', command=self.inputbox.edit_redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label='Cut           Ctrl+X')
        self.edit_menu.add_command(label='Copy        Ctrl+C')
        self.edit_menu.add_command(label='Paste        Ctrl+V')
        self.menu.add_cascade(label='Edit', menu=self.edit_menu)
        self.translate_menu = tk.Menu(self.menu, tearoff=False)
        self.translate_menu.add_command(label='Assemble         Ctrl+Enter', command=self.assemble)
        self.menu.add_cascade(label='Translate', menu=self.translate_menu)
        self.help_menu = tk.Menu(self.menu, tearoff=False)
        self.help_menu.add_command(label='Usage Help...', command=self.help)
        self.help_menu.add_command(label='About...', command=self.about)
        self.menu.add_cascade(label='Help', menu=self.help_menu)
        self.master.config(menu=self.menu)

    def create_hotkey(self):
        self.master.bind('<Control-n>', self._new)
        self.master.bind('<Control-o>', self._open)
        self.master.bind('<Control-s>', self._save)
        self.master.bind('<Control-q>', self._quit)
        self.master.bind('<Control-Return>', self._assemble)

    def new(self):
        if not self.save_changed():
            return
        self.inputbox.delete(1.0, 'end')
        self.filepath = ''
        self.filename = 'Untitled'
        self.input_text = self.inputbox.get(1.0, 'end')
        self.file_saved = True

    def open(self):
        temp = fd.askopenfilename(filetypes=[('.asm', '.asm')])
        if temp:
            if not self.save_changed():
                return
            self.filepath = temp
            self.filename = os.path.basename(self.filepath)
            self.infobox.config(state=tk.NORMAL)
            self.infobox.delete(1.0, 'end')
            self.infobox.insert('insert', 'Opening {}...\n'.format(self.filepath))
            input_text = open_file(self.filepath)
            self.inputbox.delete(1.0, 'end')
            self.inputbox.insert('insert', ''.join(input_text))
            self.input_text = self.inputbox.get(1.0, 'end')
            self.infobox.insert('insert', '- Done')
            self.infobox.config(state=tk.DISABLED)
            self.file_saved = True

    def save_file(self, save_as=False):
        if save_as:
            temp = fd.asksaveasfilename(filetypes=[('.asm', '.asm')])
        else:
            temp = self.filepath
        if temp:
            self.filepath = temp
            self.input_text = self.inputbox.get(1.0, 'end')
            self.infobox.config(state=tk.NORMAL)
            self.infobox.delete(1.0, 'end')
            self.infobox.insert('insert', 'Saving to {}...\n'.format(self.filepath))
            try:
                with open(self.filepath, 'w', encoding='utf-8') as asmfile:
                    asmfile.write(self.input_text)
                self.filename = os.path.basename(self.filepath)
                self.infobox.insert('insert', '- Done')
                self.file_saved = True
            except IOError:
                self.infobox.insert('insert', '- Failed')
            self.infobox.config(state=tk.DISABLED)
            return True
        else:
            return False

    def save(self):
        if self.filepath:
            return self.save_file(save_as=False)
        else:
            return self.save_file(save_as=True)

    def save_as(self):
        return self.save_file(save_as=True)

    def save_result(self):
        self.outputbox.config(state=tk.NORMAL)
        output_text = self.outputbox.get(1.0, 'end').strip().split('\n')
        save_result(output_text, ''.join(self.filepath.split('.')[:-1]) + '.bin')
        self.outputbox.config(state=tk.DISABLED)

    def assemble(self):
        input_text = self.inputbox.get(1.0, 'end')[:-1]
        if input_text:
            self.save()
            self.infobox.config(state=tk.NORMAL)
            self.outputbox.config(state=tk.NORMAL)
            self.outputbox.delete(1.0, 'end')
            self.infobox.delete(1.0, 'end')
            time.sleep(0.01)
            input_text = input_text.split('\n')
            success, assemble_info, results = assemble(input_text)
            assemble_info[0] = 'Assembling {}...'.format(self.filepath)
            self.infobox.insert('insert', '\n'.join(assemble_info))
            if success:
                self.outputbox.insert('insert', '\n'.join(results) + '\n')
                self.save_result()
            self.infobox.config(state=tk.DISABLED)
            self.outputbox.config(state=tk.DISABLED)

    def help(self):
        message = 'Welcome! This is a LC-3 assembler.\n\n' \
                  'If you haven\'t known about LC-3, it\'s hard for ' \
                  'you to know what this little tool exactly do.\n\n' \
                  'It\'s easy to use this little tool.Just enter ' \
                  'a LC-3 assemble language program in the `Editor` box or ' \
                  'click `Open` button toopen an existing file and ' \
                  'click the `Assemble` button, then you will see the assemble information ' \
                  'in the `info` box below. And if there is no error in your program, you will ' \
                  'also get the assemble result(in machine language) in the `Output` box.\n\n' \
                  'Following is a minimal example for you to use:\n\n' \
                  '\t.ORIG x3000\n' \
                  '\tAND R0, R0, 0\n' \
                  '\tADD R0, R0, #10\n' \
                  '\tLD R1, TEN\n' \
                  '\tADD R0, R0, R1\n' \
                  '\tST R0, RESULT\n' \
                  'TEN\t.FILL #10\n' \
                  'RESULT\t.BLKW 1\n' \
                  '.END\n\n' \
                  'Just Enter it in the `Editor` box and enjoy this little tool!\n\n' \
                  'There may be some bugs, if you find, hope you can tell me by email.'
        self.help_window = mb.showinfo(title='Usage Help', message=message)

    def about(self):
        message = 'If you have any question when using this little tool, please contact me by email.\n' \
                  'My email: vvvliuwei@gmail.com'
        self.about_window = mb.showinfo(title='About', message=message)

    def save_changed(self):
        if not self.file_saved:
            answer = mb.askyesnocancel(self.maintitle, 'Save changed to {}'.format(self.filename))
            if answer is True:
                return self.save()
            elif answer is None:
                return False
            else:
                return True
        return True

    def set_title(self):
        self.master.title(self.maintitle+' - '+self.filename+('' if self.file_saved else ' *'))

    def check_file_saved(self):
        if self.file_saved:
            input_text = self.inputbox.get(1.0, 'end')
            if input_text != self.input_text:
                self.file_saved = False

    def showline(self):
        self.line.set('Line ' + self.inputbox.index('insert').split('.')[0])

    def always_run(self):
        self.check_file_saved()
        self.set_title()
        self.showline()
        self.after(100, self.always_run)

    def _new(self, event):
        self.new()

    def _open(self, event):
        self.open()

    def _save(self, event):
        self.save()

    def _quit(self, event):
        self.quit()

    def _assemble(self, event):
        self.assemble()


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
