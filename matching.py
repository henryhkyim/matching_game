from tkinter import *
from tkinter import simpledialog
import _thread
import time
import random
import os


class TimerLabel(Label):
  def __init__(self, master, *args, **kwargs):
    Label.__init__(self, master, *args, **kwargs)
    self.gamestart = False
    self.set_text(0)

  def set_text(self, sec):
    self.config(text='Timer: %02d:%02d' % (sec//60, sec%60))

  def run_thread(self):
    self.gamestart = True
    _thread.start_new_thread(self.start_timer, ())

  def start_timer(self):    
    self.sec = 0
    while self.gamestart:
      time.sleep(1)
      self.sec += 1
      if self.gamestart:
        self.set_text(self.sec)

  def end_timer(self):
    self.gamestart = False
    return self.sec

  def new_game(self):
    self.end_timer()
    self.set_text(0)



class RecordLabel(Label):
  def __init__(self, master, *args, **kwargs):
    Label.__init__(self, master, *args, **kwargs)
    self.record = 9999999
    self.read_record()

  def read_record(self):
    if os.path.isfile('matching_game_record.txt'):
      with open('matching_game_record.txt', 'r') as file:
        lines = file.readlines()
        if lines:
          words = lines[0].split(sep=',')
          self.set_record(words[0], int(words[1]))

  def set_record(self, new_record_by, new_record):
    if self.record == 0 or self.record > new_record:
      self.record_by = new_record_by
      self.record = new_record
      self.config(text='Record by %s: %02d:%02d'%(self.record_by, self.record//60, self.record%60))
      with open('matching_game_record.txt', 'w') as file:
        file.write('%s,%d'%(new_record_by, new_record))

  def get_record(self):
    return self.record


class GameButton(Frame):
  def __init__(self, master, text, callback, img, *args, **kwargs):
    Frame.__init__(self, master, *args, **kwargs)
    self.grid_propagate(False)
    self.rowconfigure(0, weight=1)
    self.columnconfigure(0, weight=1)
    self.button = Button(self, text=text, font="Calibri 16 bold", command=self.flip_image, bg='#ccffcc', fg='#666699')
    self.button.grid(row=0, column=0, sticky='nswe')
    self.text = text
    self.callback = callback
    self.img = img
    self.selected = False
    self.gamestart = False

  def set_gamestart(self):
    self.gamestart = True

  def flip_image(self):
    if not self.selected:
      # print('selected ', self.text)
      self.selected = True
      self.image = PhotoImage(file='%d.png' % self.img)
      self.button.config(image=self.image)
      self.callback(self.text)

  def reset_button(self):
    # print('resetting ', self.text)
    if self.selected:
      self.selected = False
      self.button.config(image='')

  def new_game(self, img):
    self.img = img
    self.gamestart = False
    self.reset_button()


class GameBoard(Frame):
  def __init__(self, master, size, *args, **kwargs):
    Frame.__init__(self, master, *args, **kwargs)
    self.size = size
    self.gamebuttons = list()
    (self.gameboard, self.matched) = self.init_game(self.size)
    self.currentPick = '0'
    self.init_menu()
    self.init_gamebuttons()
    self.init_statusbar()
    self.grid_rowconfigure(0, weight=1)
    self.grid_rowconfigure(size + 1, weight=1)
    self.grid_columnconfigure(0, weight=1)
    self.grid_columnconfigure(size + 3, weight=1)
    self.gamestart = False

  def init_game(self, size):
    gameboard = list()
    for _ in range(2):
      for i in range(size*size//2):
        gameboard.append(i)
    random.shuffle(gameboard)
    matched = [False for i in range(size*size)]
    # print('gameboard', gameboard)
    return (gameboard, matched)

  def init_menu(self):
    menu_frame = Frame(self, bg='#e6f3ff', padx=2, pady=2)
    menu_frame.grid(row=1, column=1, columnspan=self.size)
    button_font = ('Calibri', 10, 'bold')
    label_font = ('Calibri', 12)
    self.new_game_button = Button(menu_frame, text='New Game', font=button_font, command=self.new_game)
    self.timer_label = TimerLabel(menu_frame, font=label_font, bg='#e6f3ff', fg='blue')
    self.record_label = RecordLabel(menu_frame, font=label_font, bg='#e6f3ff', fg='red')
    self.new_game_button.pack(side=LEFT, padx=5)
    self.timer_label.pack(side=RIGHT, padx=2)
    self.record_label.pack(side=RIGHT, padx=2)

  def init_gamebuttons(self):
    count = 1
    for i in range(2, self.size + 2):
      for j in range(1, self.size + 1):
        gb = GameButton(self, text=str(count), callback=self.gameboard_callback, img=self.gameboard[count-1], width=50, height=50)
        gb.grid(row=i, column=j, padx=2, pady=2, sticky=NSEW)
        self.gamebuttons.append(gb)
        count += 1

  def init_statusbar(self):
    label_font = ('Calibri', 12)
    self.status_label = Label(self, text='', font=label_font, bg='#e6f3ff', fg='green')
    self.status_label.grid(row=self.size + 2, column=1, columnspan=self.size)

  def new_game(self):
    (self.gameboard, self.matched) = self.init_game(self.size)
    for i, gb in enumerate(self.gamebuttons):
      gb.new_game(self.gameboard[i])
    self.timer_label.new_game()
    self.currentPick = "0"
    self.gamestart = False
    self.set_status('A new game started')

  def set_status(self, text):
    self.status_label.config(text=text)

  def gameboard_callback(self, picked):
    if not self.gamestart:
      self.gamestart = True
      self.timer_label.run_thread()
      for gb in self.gamebuttons:
        gb.set_gamestart()
    self.set_status('You picked ' + picked)
    first = self.gameboard.index(self.gameboard[int(picked)-1])
    second = self.gameboard.index(self.gameboard[int(picked)-1], first+1)
    # print('Hint: %d, %d' % (first + 1, second + 1))
    if self.currentPick == '0':
      self.currentPick = picked
    elif self.currentPick != picked:
      if self.gameboard[int(self.currentPick)-1] == self.gameboard[int(picked)-1]:
        self.matched[int(self.currentPick)-1] = True
        self.matched[int(picked)-1] = True
        num_of_pairs_left = len([m for m in self.matched if not m]) // 2
        if num_of_pairs_left == 0:
          sec = self.timer_label.end_timer()
          word = 'took'
          if sec < self.record_label.get_record():
            word = 'made a new record'
          if sec > 60:
            self.set_status('Congratulations! You %s %d mins %d secs!' % (word, sec//60, sec%60))
          else:
            self.set_status('Congratulations! You %s %d secs!' % (word, sec))
          if sec < self.record_label.get_record():
            name = simpledialog.askstring(title='Congratulations',
                                   prompt='You made a new record, please input your name: ')
            self.record_label.set_record(name, sec)
        else:
          self.set_status('Good job, %d more pair(s) to go!' % num_of_pairs_left)
      else:
        self.thread_reset_buttons(self.currentPick, picked)
        self.set_status('Sorry, try again!')
      self.currentPick = '0'

  def thread_reset_buttons(self, currentPick, picked):
    _thread.start_new_thread(self.reset_buttons_in_a_sec, (currentPick, picked))

  def reset_buttons_in_a_sec(self, currentPick, picked):
    time.sleep(1)
    self.gamebuttons[int(currentPick)-1].reset_button()
    self.gamebuttons[int(picked)-1].reset_button()


class MatchingGame(Tk):
  SIZE = 6
  def __init__(self, *args, **kwargs):
    Tk.__init__(self, *args, **kwargs)
    gameboard = GameBoard(self, self.SIZE, bg='#e6f3ff', padx=2, pady=2)
    gameboard.pack(fill='x', padx=2, pady=2)

if __name__ == '__main__':
  app = MatchingGame()
  app.title("Matching Game")
  app.geometry('430x386') # size = 6
  # app.geometry('424x454') # size = 8
  app.mainloop()
