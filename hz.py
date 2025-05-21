from customtkinter import *
import threading 
import socket

class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(("5.tcp.eu.ngrok.io", 18841))
        except Exception as e:
            print(f"не вдалось підключитись до сервера: {e}")
            



        self.frame = CTkFrame(self, width=200, height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width = 0)
        self.frame.place(x = 0, y = 0)
        self.is_show_menu = False #Флажок
        self.frame_width = 0


        self.label = CTkLabel(self.frame, text= "Type your name here:")
        self.label.pack(pady = 30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack(pady = 10)


        self.label_theme = CTkOptionMenu(self.frame, values = ["Dark", "Light"],button_color="grey",fg_color="black", command=self.change_theme)
        self.label_theme.pack(pady = 20, side = "bottom")
        self.theme = None # Пустота


        self.btn = CTkButton(self, text = "Menu", width = 150, height= 30,fg_color="black",hover_color="white",text_color="blue", command=self.showMenu)
        self.btn.place(x = 0, y = 0)
        self.menu_show_speed = 20 #На ск швидко буде відкриватись та закриватись менюшка


        self.chat_field = CTkScrollableFrame(self, )
        self.chat_field.place(x=0, y=30)
       


        self.message_input = CTkEntry(self, placeholder_text='Введіть повідомлення:')
        self.message_input.place(x=0, y=250)
        self.send_button = CTkButton(self, text='▶',fg_color="black",text_color="blue", width=40, height=30,command=self.send_message)
        self.send_button.place(x=200, y=250)

        self.username = self.entry.get() or "Kunigami"
        try:
            hello =f"TEXT@{self.username}@[SYSTEM]{self.username} приєднався(лася) до чату"
            self.sock.send(hello.encode("utf-8"))
        except Exception as e:
            print(f"Помилка відправки:{e}")
        self.recive_thred = threading.Thread(target = self.receive_messages, daemon=True)
        self.recive_thred.start()
        self.adaptive_ui()
    def send_message(self):  # Функція для відправки повідомлень
    # Параметри: self — об’єкт чату, щоб мати доступ до полів і сокета
        message = self.message_input.get().strip()  # Беремо текст із поля вводу, прибираємо зайві пробіли
        if not message:  # Перевіряємо, чи не порожній текст
            return  # Якщо порожній, ігноруємо (ніхто не любить порожні меми!)
        self.username = self.entry.get() or self.username  # Оновлюємо ім’я з поля або лишаємо старе
        if not self.username:  # Перевіряємо, чи є ім’я
            self.add_message("Помилка: Введи ім'я, бро!")  # Показуємо помилку, якщо імені немає
            return  # Виходимо, бо без імені не відправляємо
        try:  # Пробуємо відправити повідомлення
            formatted_message = f"TEXT@{self.username}@{message}\n"  # Формуємо повідомлення з тегами
            self.sock.send(formatted_message.encode("utf-8"))  # Відправляємо повідомлення в байтах
            self.add_message(f"{self.username}: {message}")  # Додаємо повідомлення до свого чату
            self.message_input.delete(0, END)  # Очищаємо поле вводу для нового мему
        except Exception as e:  # Якщо голуб не долетів, показуємо помилку
            self.add_message(f"Ой, мем не долетів: {e}")  # Додаємо повідомлення про помилку в чат

    def add_message(self, message):  # Функція для додавання повідомлень у чат
        # Параметри: self — об’єкт чату, message — текст повідомлення для показу
        message_label = CTkLabel(self.chat_field, text=message, anchor="w", wraplength=300)  # Створюємо стікер із текстом
        message_label.pack(anchor="w", padx=5, pady=2)  # Клеїмо стікер у поле чату з відступами

    def receive_messages(self):  # Функція-шпигун для отримання повідомлень від сервера
        # Параметри: self — об’єкт чату, щоб мати доступ до сокета і методу add_message
        buffer = ""  # Створюємо порожній мішок для мемів
        while True:  # Шпигун працює без зупинки
            try:  # Пробуємо зловити повідомлення
                chunk = self.sock.recv(4096)  # Ловимо до 4096 байтів (великий мішок для мемів)
                if not chunk:  # Якщо нічого не прилетіло, сервер закрився
                    break  # Шпигун іде спати
                buffer += chunk.decode("utf-8")  # Перетворюємо байти на текст і додаємо в мішок
                while "\n" in buffer:  # Шукаємо повні повідомлення (з \n)
                    line, buffer = buffer.split("\n", 1)  # Розділяємо на повідомлення та залишок
                    self.handle_line(line.strip())  # Обробляємо отриманий мем
            except Exception as e:  # Якщо голуб загубився, показуємо помилку
                self.add_message(f"Голуб загубився: {e}")  # Додаємо повідомлення про помилку

                break  # Шпигун іде спати
        self.sock.close()  # Закриваємо трубку до сервера


    def handle_line(self, line):  # Функція для обробки отриманих повідомлень
        # Параметри: self — об’єкт чату, line — текст повідомлення від сервера
        if not line:  # Якщо мем порожній, ігноруємо
            return
        parts = line.split("@", 3)  # Розбиваємо мем на частини: тип, автор, текст
        if len(parts) < 3:  # Якщо мем дивний, показуємо як є
            self.add_message(line)  # Додаємо його в чат
            return
        msg_type, author, message = parts[0], parts[1], parts[2]  # Беремо тип, автора і текст
        if msg_type == "TEXT":  # Якщо це текстовий мем
            self.add_message(f"{author}: {message}")  # Показуємо в чаті як "Оля: Привіт!"
        else:  # Якщо мем незвичайний, показуємо як є
            self.add_message(line)  # Додаємо його в чат

    def showMenu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu() #!!!!!!!!!!!!!!Розкоментувати
        else:
            self.is_show_menu = True
            self.open_menu()


    def open_menu(self):
        if self.frame_width <= 300:
            self.frame_width += self.menu_show_speed
            self.frame.configure(width = self.frame_width, height = self.winfo_height())
            if self.frame_width > 150:
                self.btn.configure(width = self.frame_width)
            self.after(20, self.open_menu)


    def close_menu(self): #!!!!Назва
        if self.frame_width >= 0: #!!!!! Змінити на  >=0
            self.frame_width -= self.menu_show_speed #!!!Змінити + на -
            self.frame.configure(width = self.frame_width, height = self.winfo_height())
            if self.frame_width > 150:
                self.btn.configure(width = self.frame_width)
            self.after(20, self.close_menu) #!!!!Змінити на close_menu
   
    def change_theme(self, value):
        if value == 'Dark':
            set_appearance_mode('dark')
        else:
            set_appearance_mode('light')


    def adaptive_ui(self):
        self.chat_field.place(x=self.frame.winfo_width() - 1)
        self.chat_field.configure(width=self.winfo_width()-self.frame.winfo_width() - 20,
                                 height=self.winfo_height()-40)
        self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.send_button.winfo_width())
        self.message_input.place(x=self.frame.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())
        self.send_button.place(x=self.winfo_width()-self.send_button.winfo_width(), y=self.winfo_height()-self.send_button.winfo_height())
        self.after(20, self.adaptive_ui)


win = MainWindow()
win.mainloop()
