#Импорт необходимых библиотек
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from PIL import Image
from imutils import contours
import cv2
import imutils
from kivy.graphics import Line, Fbo

global sourceimg
#Объявление классов, которые будут являться окнами нашего приложения

#Главное окно приложения
class MainMenu(Screen):

    pass

#Окно выбора изображения
class Filechooser(Screen):
    def select(self, *args):
        try:
            sourceimg = args[1][0]
            print(sourceimg)
        except:
            pass

#Окно справки
class HowToUse(Screen):

    pass

#Окно обводки ямы
class SelectPit(Screen):

    def on_touch_down(self, touch):
        with self.canvas:
            touch.ud["line"] = Line(points=(touch.x, touch.y), width=2)
        return super(SelectPit, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        touch.ud["line"].points += (touch.x, touch.y)
        return super(SelectPit, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        return super(SelectPit, self).on_touch_up(touch)

    def undo(self):
        item = self.objects.pop(-1)
        self.undolist.append(item)
        self.canvas.remove(item)

    def save(self, obj):
        fbo = Fbo()
        fbo.add(self.canvas)
        fbo.draw()
        img = Image.frombytes('RGBA', self.size, fbo.pixels)
        img.save('img.png')

    pass

#Окно расчета площади ямы
class CalculateObject(Screen):
    def importimage(self):
        srcimg = cv2.imread('pit.png')  #импортируем изображение с обведенной ямой
        gray = cv2.cvtColor(srcimg, cv2.COLOR_BGR2GRAY) #переводим изображение в черно-белый формат
        gray = cv2.GaussianBlur(gray, (9, 9), 0) #накладываем на изображение фильтр гаусса
        edged = cv2.Canny(gray, 50, 200) #применяем на изображение детектор углов Canny
        edged = cv2.dilate(edged, None, iterations=1)
        edged = cv2.erode(edged, None, iterations=1)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #поиск контуров на изображении
        cnts = imutils.grab_contours(cnts)
        (cnts, _) = contours.sort_contours(cnts)
        print('Количество пикселей в самом левом контуре:', len(cnts[0]), 'Площадь (на картинке):', cv2.contourArea(cnts[0]))
        points_max_cnts = 0  # количество точек в контуре (пикселей)
        indx_max_cnts = 0  # индекс самого большого контура
        #цикл сортировки границ от левого к правому краю
        for i, c in enumerate(cnts):
            if points_max_cnts < len(c):
                points_max_cnts = len(c)
                indx_max_cnts = i
        print('Количество пикселей в наибольшем контуре:', points_max_cnts, 'Индекс  контура:', indx_max_cnts,
              'Площадь (на картинке):', cv2.contourArea(cnts[indx_max_cnts]))
        orig = srcimg.copy()
        cv2.fillPoly(orig, [cnts[0]], 0) #закрашивание контура листа бумаги
        cv2.fillPoly(orig, [cnts[indx_max_cnts]], 255) #закрашивание контура ямы
        pitsize = 623.7 * cv2.contourArea(cnts[indx_max_cnts]) / cv2.contourArea(cnts[0]) #расчет площади ямы
        print('Площадь ямы:', pitsize, 'см')
        font = cv2.FONT_HERSHEY_TRIPLEX
        org = (10, 30)
        fontScale = 0.6
        color = (0, 255, 0)
        thickness = 1
        cv2.imshow('test',edged)
        cv2.putText(orig, 'Pit area: ' + '{:.1f}cm^2'.format(pitsize),
                    org, font, fontScale, color, thickness, cv2.LINE_AA) #наложение на изображение текста с площадью ямы
        cv2.imwrite('result.png', orig) #сохранение изображения с выведенной на нем площадью
    pass

# окно камеры (работает некорректно)
# class CameraClick(Screen):
#      def capture(self):
#          camera = self.ids['camera']
#          timestr = time.strftime("%Y%m%d_%H%M%S")
#          camera.export_to_png("IMG_{}.png".format(timestr))
#          print("Captured")

#окно с конечным результатом
class Result(Screen):

    pass

class Devs(Screen):

    pass

#главный класс kivy
class MyApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(Filechooser(name='chooser'))
        sm.add_widget(SelectPit(name='selectpit'))
        sm.add_widget(CalculateObject(name='calcobj'))
        sm.add_widget(Result(name='result'))
        sm.add_widget(HowToUse(name='htu'))
        sm.add_widget(Devs(name='devs'))
#        sm.add_widget(CameraClick(name='camera'))
        self.title = 'RoadMaster'
        return sm

if __name__ == '__main__':
    MyApp().run()