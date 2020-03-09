from PIL import Image, ImageFilter
import sys

import pygame

WINDOW_SIZE = (1920, 1080)


class SpritesData:
	def __init__(self, sprites_data_list):
		super(SpritesData, self).__init__()
		self.sprites_data_list = sprites_data_list

	def search(self, name):
		data_id = None 
		# Ищем спрайт по его названию
		for num in range(len(self.sprites_data_list)):
			if name == self.sprites_data_list[num][0]:
				data_id = num # Присваиваем индекс с данными спрайта
		return data_id

	def add(self, name, size, position):
		# Удаляем данные о спрайте если они есть
		if self.search(name) != None:
			self.delete(name)
		# Добавляем новые данные о спрайте
		self.sprites_data_list.append([name, size, position])

	def read(self, name):
		data_id = self.search(name) # Ищем данные спрайта
		# Присваиваем значения спрайта
		size = self.sprites_data_list[data_id][1]
		position = self.sprites_data_list[data_id][2]
		return size, position

	def delete(self, name):
		data_id = self.search(name) # Ищем данные спрайта
		self.sprites_data_list.pop(data_id) # Удаляем данные о спрайте

class Sprite:
	def __init__(self, sprites_data_list):
		super(Sprite, self).__init__()
		self.sprites_data_list = sprites_data_list

	def get_size(self, name, url, img):
		wsize = WINDOW_SIZE

		# Получаем адаптированный размер спрайиа
		if name == 'main_bg.png':
			size = (int((int(wsize[1]*1.2)/img.size[1])*img.size[0]), int(wsize[1]*1.2))

		elif name == 'front_bg.png':
			temp_size = self.get_size(name='main_bg.png', url=url,
									  img=Image.open(url + 'main_bg.png'))
			size = (int(temp_size[0]+temp_size[0]/6),
					int((int(temp_size[0]+temp_size[0]/6)/img.size[0])*img.size[1]))

		elif name == 'character.png':
			size = [int((int(wsize[1]/2.5)/img.size[1])*img.size[0]), int(wsize[1]/2.5)]

		elif name == 'bg_menu.png':
			size = (int((wsize[1]/img.size[1])*img.size[0]), wsize[1])

		return size

	def adapt(self, name, url, isBlur=False):
		img = Image.open(url + name) # Открываем изображение
		size = self.get_size(name, url, img) # Получаем адаптированный размер
		img.thumbnail(size) # Изменяем размер изображения
		
		# Размытие изображения
		if isBlur:
			img = img.filter(ImageFilter.BoxBlur(5))

		img.save(url + 'Temp/' + name, 'PNG') # Сохраняем изменённое изображение
		return size

	def add(self, name, url, isAlpha=False):
		wsize = WINDOW_SIZE
		sprites_data = SpritesData(self.sprites_data_list)

		# Получаем размер и позицию спрайта
		if name == 'bg_menu.png':
			size = self.adapt(name=name, url=url)
			position = (wsize[0]-size[0], 0)

		elif name == 'main_bg.png':
			size = self.adapt(name=name, url=url)
			position = [int((wsize[0]-size[0])/2), int((wsize[1]-size[1])/2)]

		elif name == 'front_bg.png':
			size = self.adapt(name=name, url=url, isBlur=True)
			position = [int((wsize[0]-size[0])/2), int(wsize[1]-(size[1])+(size[1]/4))]

		elif name == 'character.png':
			size = self.adapt(name=name, url=url)
			position = [200, int((wsize[1]-size[1])/2)]

		sprites_data.add(name, size, position) # Добавляем данные спрайта
		sprite = pygame.image.load(url + 'Temp/' + name) # Загружаем спрайт
		sprite = pygame.transform.scale(sprite, size) # Указываем размер спрайта

		# Конвертировать альфа канал
		if isAlpha:
			sprite = sprite.convert_alpha()
		else:
			sprite = sprite.convert()
		return sprite

	def update(self, sprite, name, screen):
		sprites_data = SpritesData(self.sprites_data_list)
		size, position = sprites_data.read(name) # Присваиваем данные спрайта
		screen.blit(sprite, position) # Добавляем спрайт в гл.поверхность
		return screen

class Character:
	def __init__(self, sprites_data_list):
		super(Character, self).__init__()
		self.sprites_data_list = sprites_data_list

	def moving(self, mouse_position):
		speed = 1 # Задаём скорость персонажа
		sprites_data = SpritesData(self.sprites_data_list)
		size, position = sprites_data.read('character.png') # Получаем данные спрайта
		# Находим текущую позицию персонажа
		current_position = [position[0]+int(size[0]/2), position[1]+size[1]]

		# Персонаж достиг цели
		if current_position[0] == mouse_position[0] and\
		   current_position[1] == mouse_position[1]:
			return False

		# Перемещение персонажа
		if current_position[0] > mouse_position[0]:
			position[0] = position[0]-speed # Влево

		elif current_position[0] < mouse_position[0]:
			position[0] = position[0]+speed # Вправо

		if current_position[1] > mouse_position[1]:
			position[1] = position[1]-speed # Вверх

		elif current_position[1] < mouse_position[1]:
			position[1] = position[1]+speed # Вниз
		# Добавляем новые данные спрайта
		sprites_data.add('character.png', size, [position[0], position[1]])
		return True

class Camera:
	def __init__(self, sprites_data_list):
		super(Camera, self).__init__()
		self.sprites_data_list = sprites_data_list
	
	def moving(self):
		w_size = WINDOW_SIZE
		sprites_data_list = self.sprites_data_list
		sprites_data = SpritesData(sprites_data_list)
		mbg = sprites_data_list[sprites_data.search('main_bg.png')]
		char = sprites_data_list[sprites_data.search('character.png')]
		fbg = sprites_data_list[sprites_data.search('front_bg.png')]

		# Перемещение фона
		if char[2][0]+char[1][0] > w_size[0]*0.8\
				and mbg[2][0] > (w_size[0]-mbg[1][0]): # Вправо
			fbg[2][0] -= 2
			mbg[2][0] -= 1
			char[2][0] -= 1

		if char[2][0] < w_size[0]*0.2 and not mbg[2][0] >= 0: # Влево
			fbg[2][0] += 2
			mbg[2][0] += 1
			char[2][0] += 1

		if char[2][1]+char[1][1] > w_size[1]*0.8\
				and mbg[2][1] > (w_size[1]-mbg[1][1]): # Вниз
			fbg[2][1] -= 1.5
			mbg[2][1] -= 1
			char[2][1] -= 1
		
		if char[2][1] < w_size[1]*0.2 and not mbg[2][1] >= 0: # Вверх
			fbg[2][1] += 1.5
			mbg[2][1] += 1
			char[2][1] += 1

class Button:
	def __init__(self):
		super(Button, self).__init__()

	def update(self, position, size, item):
		mp = pygame.mouse.get_pos() # Получаем позицию мыши
		# Если курсор находится на кнопке изменяем её параметр
		if mp[0]>position[0] and mp[0]<position[0]+size[0] and\
		   mp[1]>position[1] and mp[1]<position[1]+size[1]:
			item[2] = 1
		else:
			item[2] = 0

	def add(self, items, surface):
		color = (60, 47, 126) # Цвет кнопки
		# Получаем размер и позицию кнопок
		size = [int(WINDOW_SIZE[0]/5.5), int(WINDOW_SIZE[1]/20)]
		position = [int(WINDOW_SIZE[0]/30), int(WINDOW_SIZE[1]*0.9)]
		# Подключаем шрифт
		font = pygame.font.Font('bin/Fonts/Nunito-Regular.ttf', int(size[1]*0.75))
		for item in items[::-1]:
			self.update(position, size, item) # Обновляем события кнопки
			# Создаём кнопку
			if item[2]: # Если курсор на кнопке
				rec = pygame.Rect(position, (int(size[0]*1.1), size[1]))
			else:
				rec = pygame.Rect(position, size)
			pygame.draw.rect(surface, color, rec, 3) # Добавляем кнопку в гл.поверхность
			# Добавляем текст кнопки в гл.поверхность
			surface.blit(font.render(item[0], 1, color),
						(int(position[0]*1.1), position[1]))
			position[1] = int(position[1]-size[1]*1.3) # Изменяем позицию следующей кнопки

class EventHandling:
	def __init__(self, sprites_data_list, events_list):
		super(EventHandling, self).__init__()
		self.sprites_data_list = sprites_data_list
		self.events_list = events_list

	def search(self, event_name):
		event_id = None 
		# Ищем событие по его названию
		for num in range(len(self.events_list)):
			if event_name == self.events_list[num][0]:
				event_id = num # Присваиваем индекс события
		return event_id

	def add(self, new_events):
		self.events_list.append(new_events) # Добавляем новое событие

	def delete(self, event_name):
		index = self.search(event_name) # Получаем индекс события из списка
		if index != None:
			self.events_list.pop(index) # Удаляем событие из списка

	def handling(self, new_events):
		# Добавляем все новые события
		for event in new_events:
			if self.search(event[0]) == None:
				self.add(event)
			else:
				self.delete(event[0])
				self.add(event)

	def activation(self):
		for event in self.events_list:
			if event[0] == 'character_moving':
				character = Character(self.sprites_data_list)
				isMoving = character.moving(event[1])
				if not isMoving:
					self.delete(event[0])

class LocationScreen:
	def __init__(self, window, sprites_data_list, events_list):
		super(LocationScreen, self).__init__()
		self.window = window
		self.events_list = events_list
		self.sprites_data_list = sprites_data_list

	def update(self):
		new_events = []
		for event_element in pygame.event.get():
			# Кнопка выхода
			if event_element.type == pygame.QUIT:
				sys.exit()

			if event_element.type == pygame.KEYDOWN:
				# Кнопка выхода
				if event_element.key == pygame.K_ESCAPE:
					sys.exit()

			# Нажатие на мышку
			if event_element.type == pygame.MOUSEBUTTONDOWN:
				mouse_position = pygame.mouse.get_pos() # Получаем позицию мыши
				# Добавляем событие ходьбы персонажа
				new_events.append(['character_moving', mouse_position])

		return new_events

	def location(self):
		done = True # Ключ цикла
		FPS = 60 # Максимальная частота кадров
		url = 'bin/Sprites/Location1/' # Путь к спрайтам

		window = self.window
		events_list = self.events_list
		sprites_data_list = self.sprites_data_list

		screen = pygame.Surface(WINDOW_SIZE) # Создаём главную поверхность
		clock = pygame.time.Clock() # Отслеживаем время
		font = pygame.font.Font(None, 60) # Добавляем шрифт
		sprite = Sprite(sprites_data_list)
		camera = Camera(sprites_data_list)
		event_handling = EventHandling(sprites_data_list, events_list)

		# Добавляем спрайты
		sprite_mbg = sprite.add(name='main_bg.png', url=url)
		sprite_chr = sprite.add(name='character.png', url=url, isAlpha=True)
		sprite_fbg = sprite.add(name='front_bg.png', url=url, isAlpha=True)

		# Основной цикл игры
		while done:
			screen.fill((20, 20, 20)) # Добавляем цвет фона
			# Создаём счётчик FPS
			fps = font.render(str(int(clock.get_fps())), True, pygame.Color('red'))

			new_events = self.update() # Проверяем новые события
			event_handling.handling(new_events) # Обновляем лист событий
			event_handling.activation() # Активируем события

			# Обновляем спрайты
			sprite.update(sprite_mbg, 'main_bg.png', screen)
			sprite.update(sprite_chr, 'character.png', screen)
			sprite.update(sprite_fbg, 'front_bg.png', screen)
			camera.moving()

			screen.blit(fps, (50, 50)) # Добавляем счётчик FPS в гл.поверхность
			window.blit(screen, (0, 0)) # Добавляем гл.поверхность в окно
			pygame.display.flip() # Обновление дисплея
			clock.tick(FPS) # Ограничиваем число кадров

class MenuScreen:
	def __init__(self, window, sprites_data_list, events_list):
		super(MenuScreen, self).__init__()
		self.window = window
		self.events_list = events_list
		self.sprites_data_list = sprites_data_list

	def loading(self, screen):
		screen.fill((230, 230, 255)) # Добавляем цвет фона
		font = pygame.font.Font('bin/Fonts/Nunito-Regular.ttf', 120) # Подключаем шрифт
		text = font.render(u'Loading...', 1, (180, 180, 205)) # Добавляем текст
		center = (int(WINDOW_SIZE[0]/2), int(WINDOW_SIZE[1]/2)) # Находим центр экрана
		position = text.get_rect(center=center) # Находим позицию текста
		screen.blit(text, position) # Добавляем текст в гл.поверхность

	def update(self, done, list_buttons):
		for event_element in pygame.event.get():
			if event_element.type == pygame.KEYDOWN:
				# Кнопка выхода
				if event_element.key == pygame.K_ESCAPE:
					sys.exit()

			# Нажатие на один из пунктов в меню
			if event_element.type == pygame.MOUSEBUTTONDOWN and event_element.button == 1:
				for button in list_buttons:
					# Кнопка запуска игры
					if button[2] and button[1] == 1:
						done = False
					# Кнопка выхода
					elif button[2] and button[1] == 2:
						sys.exit()
		return done

	def menu_screen(self):
		done = True # Ключ цикла
		FPS = 60 # Максимальная частота кадров
		url = 'bin/Sprites/MainMenu/' # Путь к спрайтам

		window = self.window
		events_list = self.events_list
		sprites_data_list = self.sprites_data_list

		screen = pygame.Surface(WINDOW_SIZE) # Создаём главную поверхность
		clock = pygame.time.Clock() # Отслеживаем время
		sprite = Sprite(sprites_data_list)
		button = Button()

		# Добавляем спрайт
		sprite_mbg = sprite.add(name='bg_menu.png', url=url, isAlpha=True)

		# Список кнопок (text, id, cursor)
		list_buttons = [[u'Game', 1, 0],
						[u'Exit', 2, 0]]

		# Основной цикл игры
		while done:
			screen.fill((230, 230, 255)) # Добавляем цвет фона

			done = self.update(done, list_buttons) # Проверяем новые события

			# Обновляем спрайт
			sprite.update(sprite_mbg, 'bg_menu.png', screen)
			button.add(list_buttons, screen) # Добавляем кнопки
			
			# Добавить загрузочный экран в гл.поверхность
			if not done:
				self.loading(screen)

			window.blit(screen, (0, 0)) # Добавляем гл.поверхность в окно
			pygame.display.flip() # Обновление дисплея
			clock.tick(FPS) # Ограничиваем число кадров

class Main:
	def __init__(self):
		super(Main, self).__init__()

	def start(self, window, screen):
		sprites_data_list = [] # Создаём новый список данных спрайтов
		events_list = [] # Создаём новый список событий

		if screen == 'menu':
			game_screen = MenuScreen(window, sprites_data_list, events_list)
			game_screen.menu_screen()

		elif screen == 'location':
			game_screen = LocationScreen(window, sprites_data_list, events_list)
			game_screen.location()

	def load_window(self):
		# Создаём окно игры
		window = pygame.display.set_mode(WINDOW_SIZE,
			pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)
		pygame.display.set_caption('Summer')

		pygame.font.init() # Инициализация шрифтов

		self.start(window, 'menu') # Запускаем главное меню
		self.start(window, 'location') # Запуск игры

		pygame.font.quit() # Отключение шрифтов

	def main(self):
		self.load_window()

if __name__ == '__main__':
	main_class = Main()
	main_class.main()