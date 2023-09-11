import ctypes
import inspect
from math import ceil
import pymprog
import threading
from time import time
import tkinter as tk
from tkinter import ttk


class GUI:
    def __init__(self, root):
        self.root = root
        self.topOpen = False
        self.root.resizable(False, False)
        self.root.title('Cutting-Stock Problem')
        self.showMainScreen()

    def showMainScreen(self):
        self.mainFrame = tk.Frame(self.root)
        self.mainFrame.pack()

        self.topFrame = tk.Frame(self.mainFrame)
        self.topFrame.pack(fill='x')

        self.ordersLabel = tk.Label(self.topFrame, text='Orders:', font='Arial 14')
        self.ordersLabel.pack(anchor='nw', padx=5)

        self.tableFrame = tk.Frame(self.mainFrame)
        self.tableFrame.pack(fill='x')

        self.tableScroll = tk.Scrollbar(self.tableFrame)
        self.tableScroll.pack(side='right', fill='y')

        self.table = ttk.Treeview(self.tableFrame, yscrollcommand=self.tableScroll.set)

        self.table['columns'] = ('length', 'amount')

        self.table.column('#0', width=0, stretch='no')
        self.table.column('length', anchor='center')
        self.table.column('amount', anchor='center')

        self.table.heading('#0', text='', anchor='center')
        self.table.heading('length', text='Length', anchor='center')
        self.table.heading('amount', text='Amount', anchor='center')

        self.table.insert(parent='', index='end', values=(1380, 22))
        self.table.insert(parent='', index='end', values=(1520, 25))
        self.table.insert(parent='', index='end', values=(1560, 12))
        self.table.insert(parent='', index='end', values=(1710, 14))
        self.table.insert(parent='', index='end', values=(1820, 18))
        self.table.insert(parent='', index='end', values=(1880, 18))
        self.table.insert(parent='', index='end', values=(1930, 20))
        self.table.insert(parent='', index='end', values=(2000, 10))
        self.table.insert(parent='', index='end', values=(2050, 12))
        self.table.insert(parent='', index='end', values=(2100, 14))
        self.table.insert(parent='', index='end', values=(2140, 16))
        self.table.insert(parent='', index='end', values=(2150, 18))
        self.table.insert(parent='', index='end', values=(2200, 20))

        self.table.pack(fill='x')

        self.tableScroll.config(command=self.table.yview)

        self.optionsFrame = tk.Frame(self.mainFrame)
        self.optionsFrame.pack(fill='x')

        self.optionsFrame.grid_columnconfigure(0, weight=1)
        self.optionsFrame.grid_columnconfigure(1, weight=1)

        self.addRowButton = tk.Button(self.optionsFrame, text='Add Row', command=self.openAddRow, relief='groove')
        self.addRowButton.grid(row=0, column=0, pady=10)

        self.widthFrame = tk.Frame(self.optionsFrame)
        self.widthFrame.grid(row=0, column=1, pady=10)

        self.widthLabel = tk.Label(self.widthFrame, text='Stock length')
        self.widthLabel.grid(row=0, column=0)

        self.widthEntry = tk.Entry(self.widthFrame)
        self.widthEntry.insert('end', 5600)
        self.widthEntry.grid(row=0, column=1)

        self.methodFrame = tk.LabelFrame(self.optionsFrame, text='Method')
        self.methodFrame.grid(row=1, column=0, pady=(0, 10))

        self.method = tk.IntVar(None, 1)
        self.methodRadio1 = tk.Radiobutton(self.methodFrame, text='Generate all patterns initially (slow)', variable=self.method, value=1)
        self.methodRadio1.pack(anchor='nw')

        self.methodRadio2 = tk.Radiobutton(self.methodFrame, text='Generate patterns when needed (fast)', variable=self.method, value=2)
        self.methodRadio2.pack(anchor='nw')

        self.experimentalFrame = tk.LabelFrame(self.optionsFrame, text='Experimental')
        self.experimentalFrame.grid(row=1, column=1, pady=(0, 10))

        self.useLoss = tk.IntVar(None, 0)
        self.useLossCheck = tk.Checkbutton(self.experimentalFrame, text='Minimize waste instead of stock', variable=self.useLoss)
        self.useLossCheck.pack(anchor='nw')

        self.useTight = tk.IntVar(None, 0)
        self.useTightCheck = tk.Checkbutton(self.experimentalFrame, text='Use tighter constraints', variable=self.useTight)
        self.useTightCheck.pack(anchor='nw')

        self.solveButton = tk.Button(self.optionsFrame, text='SOLVE', command=self.prepareSolve, width=20, bg='yellow', activebackground='yellow', relief='ridge')
        self.solveButton.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        self.resultsFrame = tk.Frame(self.mainFrame)
        self.resultsFrame.pack()

        self.resultsScroll = tk.Scrollbar(self.resultsFrame)
        self.resultsScroll.pack(side='right', fill='y')

        self.resultsText = tk.Text(self.resultsFrame, height=20, yscrollcommand=self.resultsScroll.set, state='disabled')
        self.resultsText.pack(side='left')

        self.table.bind('<Double-1>', self.openEditValue)
        self.table.bind('<Delete>', self.handleDeletePressed)

        self.methodRadio1.bind('<1>', lambda e: self.changeExperimentalState(1))
        self.methodRadio2.bind('<1>', lambda e: self.changeExperimentalState(0))

    def changeExperimentalState(self, state):
        if state == 0:
            self.useLoss.set(0)
            self.useTight.set(0)
        self.useLossCheck.config(state=('disabled' if state == 0 else 'normal'))
        self.useTightCheck.config(state=('disabled' if state == 0 else 'normal'))

    def handleDeletePressed(self, event):
        if self.topOpen:
            return

        self.selected_row = self.table.identify_row(event.y)
        if not self.selected_row:
            return

        self.table.delete(self.selected_row)

    def openEditValue(self, event):
        if self.topOpen:
            return

        self.selected_row = self.table.identify_row(event.y)
        if not self.selected_row:
            return

        self.topOpen = True

        self.top = tk.Toplevel(self.mainFrame)
        self.top.resizable(False, False)
        self.top.focus_set()
        self.top.grab_set()
        self.top.title('Edit Row')
        self.top.bind('<Destroy>', self.topDestroyed)
        # self.root.eval(f'tk::PlaceWindow {str(self.top)} center')

        self.values = self.table.item(self.selected_row, 'values')

        self.editMainFrame = tk.Frame(self.top)
        self.editMainFrame.pack(pady=30, padx=40)

        self.editSizeLabel = tk.Label(self.editMainFrame, text='Length: ')
        self.editSizeLabel.grid(row=0, column=0, sticky='e')

        self.editSizeEntry = tk.Entry(self.editMainFrame)
        self.editSizeEntry.insert('end', self.values[0])
        self.editSizeEntry.grid(row=0, column=1)

        self.editAmountLabel = tk.Label(self.editMainFrame, text='Amount: ')
        self.editAmountLabel.grid(row=1, column=0, sticky='e')

        self.editAmountEntry = tk.Entry(self.editMainFrame)
        self.editAmountEntry.insert('end', self.values[1])
        self.editAmountEntry.grid(row=1, column=1)

        self.editBottomFrame = tk.Frame(self.top)
        self.editBottomFrame.pack(fill='x', padx=5, pady=(0, 5))

        self.editRemoveButton = tk.Button(self.editBottomFrame, text='Remove', command=self.removeItem, width=10)
        self.editRemoveButton.pack(side='left')

        self.editOKButton = tk.Button(self.editBottomFrame, text='OK', command=self.saveChanges, width=10)
        self.editOKButton.pack(side='right')

    def saveChanges(self):
        size = self.editSizeEntry.get()
        amount = self.editAmountEntry.get()

        self.table.item(self.selected_row, values=(size, amount))

        self.top.destroy()

    def removeItem(self):
        self.table.delete(self.selected_row)

        self.top.destroy()

    def openAddRow(self):
        if self.topOpen:
            return

        self.topOpen = True

        self.top = tk.Toplevel(self.mainFrame)
        self.top.resizable(False, False)
        self.top.focus_set()
        self.top.grab_set()
        self.top.title('Add Row')
        self.top.bind('<Destroy>', self.topDestroyed)
        # self.root.eval(f'tk::PlaceWindow {str(self.top)} center')

        self.addMainFrame = tk.Frame(self.top)
        self.addMainFrame.pack(pady=30, padx=40)

        self.addSizeLabel = tk.Label(self.addMainFrame, text='Length: ')
        self.addSizeLabel.grid(row=0, column=0, sticky='e')

        self.addSizeEntry = tk.Entry(self.addMainFrame)
        self.addSizeEntry.grid(row=0, column=1)

        self.addAmountLabel = tk.Label(self.addMainFrame, text='Amount: ')
        self.addAmountLabel.grid(row=1, column=0, sticky='e')

        self.addAmountEntry = tk.Entry(self.addMainFrame)
        self.addAmountEntry.grid(row=1, column=1)

        self.addBottomFrame = tk.Frame(self.top)
        self.addBottomFrame.pack(fill='x', padx=5, pady=(0, 5))

        self.addOKButton = tk.Button(self.addBottomFrame, text='OK', command=self.addRow, width=10)
        self.addOKButton.pack(side='right')

    def addRow(self):
        size = self.addSizeEntry.get()
        amount = self.addAmountEntry.get()

        self.table.insert(parent='', index='end', values=(size, amount))

        self.top.destroy()

    def topDestroyed(self, event):
        self.topOpen = False

    def printToResults(self, text):
        self.resultsText.config(state='normal')
        self.resultsText.insert('end', text)
        self.resultsText.config(state='disabled')
        self.resultsText.see('end')
        self.resultsText.update()

    def clearResults(self):
        self.resultsText.config(state='normal')
        self.resultsText.delete(1.0, 'end')
        self.resultsText.config(state='disabled')
        self.resultsText.see('end')
        self.resultsText.update()

    def prepareSolve(self):
        self.piece_sizes = []
        self.piece_amounts = []
        # self.stock_length
        # self.method
        # self.useLoss
        # self.useTight

        try:
            for item in self.table.get_children():
                self.piece_sizes.append(int(self.table.item(item, 'values')[0]))
                self.piece_amounts.append(int(self.table.item(item, 'values')[1]))

            self.stock_length = int(self.widthEntry.get())

        except ValueError:
            return

        # print(self.piece_sizes, self.piece_amounts, self.stock_length, self.method.get())

        if not self.piece_sizes or not self.piece_amounts:
            return

        if any(s > self.stock_length for s in self.piece_sizes):
            return

        self.clearResults()
        # self.solve(self.piece_sizes, self.piece_amounts, self.stock_length, self.method.get(), self.useLoss.get(), self.useTight.get())
        solve_thread = ThreadWithExc(target=self.solve, daemon=True, args=(self.piece_sizes, self.piece_amounts, self.stock_length, self.method.get(), self.useLoss.get(), self.useTight.get()))

        self.solveButton.config(text='Cancel', command=lambda: self.cancel(solve_thread), bg='red', activebackground='red')

        solve_thread.start()

    def cancel(self, solve_thread):
        solve_thread.raiseExc(ThreadStoppedControlledException)

    def solve(self, piece_sizes, piece_amounts, stock_length, method = 1, useLoss = 0, useTight = 0):
        try:
            start = time()

            if method == 1:
                def findRightmostNonZero(A):
                    for i in range(-1, -(len(A) + 1), -1):
                        # if A[i] != 0 and i != -1:
                        if A[i] != 0:
                            return i
                    return 0

                y = []
                loss = []

                self.printToResults('Generating all patterns...')

                #  init
                x = []
                for j in range(len(piece_sizes)):
                    s = 0
                    for k in range(j):
                        s += x[k] * piece_sizes[k]
                    x.append((stock_length - s) // piece_sizes[j])

                if useLoss:
                    temp_loss = stock_length
                    for i in range(len(piece_sizes)):
                        temp_loss -= (x[i] * piece_sizes[i])
                    loss.append(temp_loss)
                y += [x[:]]

                while(True):
                    z = findRightmostNonZero(x)
                    if not z:
                        break

                    x[z] -= 1
                    for j in range(z + len(piece_sizes) + 1, len(piece_sizes)):
                        s = 0
                        for k in range(j):
                            s += x[k] * piece_sizes[k]
                        x[j] = (stock_length - s) // piece_sizes[j]

                    if useLoss:
                        temp_loss = stock_length
                        for i in range(len(piece_sizes)):
                            temp_loss -= (x[i] * piece_sizes[i])
                        loss.append(temp_loss)
                    y += [x[:]]

                # remove do-nothing pattern
                y.pop()
                if useLoss:
                    loss.pop()

                self.printToResults(f' Done!\n{len(y)} patterns generated.\n')


                self.printToResults('Solving...')
                # begin modelling
                model = pymprog.model('cutting-stock')
                # model.verbose(True)

                # variables
                x = model.var('x', len(y), bounds=(0, None), kind=int)

                # objective
                if useLoss:
                    model.minimize(sum(loss[j] * x[j] for j in range(len(y))), 'Z')
                else:
                    model.minimize(sum(x[j] for j in range(len(y))), 'Z')

                # constraints
                for i in range(len(piece_sizes)):
                    sum(y[j][i] * x[j] for j in range(len(y))) >= piece_amounts[i]

                if useTight:
                    for i in range(len(piece_sizes)):
                        sum(y[j][i] * x[j] for j in range(len(y))) <= piece_amounts[i]

                # solve the problem
                model.solve()

                model.end()

                end = time()

                self.printToResults(f' Done!\nZ = {model.vobj():.2f}\n')
                self.printToResults(self.interpretResults(x, y, piece_sizes))
                self.printToResults(f'Took {(end - start):.3f} seconds.')


            elif method == 2:
                self.printToResults('Starting delayed column generation process...')

                # generate initial patterns, enough to get a feasible solution
                y = [[((stock_length // piece_sizes[i]) if i == j else 0) for i in range(len(piece_sizes))] for j in range(len(piece_sizes))]

                while True:
                    # begin modelling
                    model = pymprog.model('cutting-stock')
                    # model.verbose(True)

                    # variables
                    x = model.var('x', len(y), bounds=(0, None))

                    # objective
                    model.minimize(sum(x[j] for j in range(len(y))), 'Z')

                    # constraints
                    R = []
                    for i in range(len(piece_sizes)):
                        R.append(sum(y[j][i] * x[j] for j in range(len(y))) >= piece_amounts[i])

                    # solve the problem
                    model.solve()

                    model.end()

                    ####################################################################
                    model2 = pymprog.model('knapsack-subproblem')

                    # variables
                    z = model2.var('z', len(piece_sizes), bounds=(0, None), kind=int)

                    # objective
                    model2.maximize(sum(R[j].dual * z[j] for j in range(len(piece_sizes))), 'Z')

                    # constraints
                    sum(piece_sizes[j] * z[j] for j in range(len(piece_sizes))) <= stock_length

                    # solve the problem
                    model2.solve()

                    if model2.vobj() < 1.0001:
                        break

                    temp = [z[j].primal for j in range(len(piece_sizes))]
                    if temp in y:
                        self.printToResults('\nStopping early because of an error...')
                        break
                    y.append(temp[:])

                    model2.end()

                self.printToResults(f' Done!\n{len(y)} patterns generated.\n')


                self.printToResults('Solving LP...')
                # begin modelling
                model = pymprog.model('cutting-stock')

                # variables
                x = model.var('x', len(y), bounds=(0, None))

                # objective
                model.minimize(sum(x[j] for j in range(len(y))), 'Z')

                # constraints
                for i in range(len(piece_sizes)):
                    sum(y[j][i] * x[j] for j in range(len(y))) >= piece_amounts[i]

                # solve the problem
                model.solve()

                model.end()

                self.printToResults(f' Done!\nZ = {model.vobj():.2f} so a minimum of {ceil(model.vobj())} master (stock) pieces are required.\n')


                self.printToResults('Solving IP...')
                # begin modelling
                model = pymprog.model('cutting-stock')

                # variables
                x = model.var('x', len(y), bounds=(0, None), kind=int)

                # objective
                model.minimize(sum(x[j] for j in range(len(y))), 'Z')

                # constraints
                for i in range(len(piece_sizes)):
                    sum(y[j][i] * x[j] for j in range(len(y))) >= piece_amounts[i]

                # solve the problem
                model.solve()

                model.end()

                end = time()

                self.printToResults(f' Done!\nFound a solution where Z = {model.vobj():.2f}\n')
                self.printToResults(self.interpretResults(x, y, piece_sizes))
                self.printToResults(f'Took {(end - start):.3f} seconds.')
        except ThreadStoppedControlledException:
            print('Thread stopped!')
            self.printToResults('\n\nSolving stopped!\n')
        finally:
            self.solveButton.config(text='Solve', command=self.prepareSolve, bg='yellow', activebackground='yellow')

    def interpretResults(self, x, y, piece_sizes):
        interpretation = ''
        for i, xi in enumerate(x):
            if xi.primal:
                temp_str = ''
                for j, val in enumerate(y[i]):
                    if val:
                        if temp_str:
                            temp_str += ' + '
                        temp_str += str(piece_sizes[j]) + int(val - 1) * (' + ' + str(piece_sizes[j]))
                interpretation += f'{int(xi.primal)} x ({temp_str})\n'
        return interpretation


# code below from: https://stackoverflow.com/a/325528
##############################################################################
def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class ThreadWithExc(threading.Thread):
    '''A thread class that supports raising an exception in the thread from
       another thread.
    '''
    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL: this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # TODO: in python 2.6, there's a simpler way to do: self.ident

        raise AssertionError("could not determine the thread's id")

    def raiseExc(self, exctype):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(),
        socket.accept(), ...), the exception is simply ignored.

        If you are sure that your exception should terminate the thread,
        one way to ensure that it works is:

            t = ThreadWithExc( ... )
            ...
            t.raiseExc( SomeException )
            while t.isAlive():
                time.sleep( 0.1 )
                t.raiseExc( SomeException )

        If the exception is to be caught by the thread, you need a way to
        check that your thread has caught it.

        CAREFUL: this function is executed in the context of the
        caller thread, to raise an exception in the context of the
        thread represented by this instance.
        """
        _async_raise( self._get_my_tid(), exctype )
##############################################################################

class ThreadStoppedControlledException(Exception):
    pass


if __name__ == '__main__':
    root = tk.Tk()
    GUI(root)
    root.mainloop()
