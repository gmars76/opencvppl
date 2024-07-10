from tkinter import PhotoImage
from PIL import Image, ImageTk
import numpy as np
import cv2 as cv
import os
import json


### TUTORIALES pyOpenCV
# https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html

# Una cosa es el ID y otra el Título (aunque por defecto el título es el ID la primera vez)
# https://stackoverflow.com/questions/48769750/images-are-opened-differently-when-changing-the-title

class CVUtils:

    DEBUG_MODE = True

    KEY_SPACE = 32
    KEY_BACKSPACE = 8
    KEY_ESCAPE = 27

    # kernel, de convolución, matriz cuadrada MxM impar, para poder centrarla en cada uno de los pixeles de la imagen original.
    KERNEL_BLUR_3 = np.ones((3, 3), np.float32) / 9
    KERNEL_BLUR_5 = np.ones((5, 5), np.float32) / 25
    KERNEL_BLUR_7 = np.ones((7, 7), np.float32) / 49
    KERNEL_BLUR_9 = np.ones((9, 9), np.float32) / 81

    # kernel de ENFOQUE duro
    KERNEL_FOCUS_HARD = np.array([ [-1, -1, -1], [-1, 9, -1], [-1, -1, -1] ])
    # kernel de ENFOQUE suave
    KERNEL_FOCUS_SOFT = np.array([ [0, -1, 0], [-1, 5, -1], [0, -1, 0] ])

    # kernel de Sobel para detección de BORDES 
    KERNEL_SOBEL_EDGE_VERT = np.array([[1,0,-1], [2,0,-2], [1,0,-1]])
    KERNEL_SOBEL_EDGE_HOR = np.array([[-1,-2,-1], [0,0,0], [1,2,1]])

    # kernels de Prewitt BORDES
    KERNEL_PREWITT_EDGE_VERT = np.array([[1,0,-1], [1,0,-1], [1,0,-1]])
    KERNEL_PREWITT_EDGE_HOR = np.array([[-1,-1,-1], [0,0,0], [1,1,1]])

    # kernels de Scharr BORDES
    KERNEL_SCHARR_EDGE_VERT = np.array([[3,0,-3], [10,0,-10], [3,0,-3]])
    KERNEL_SCHARR_EDGE_HOR = np.array([[-3,-10,-3], [0,0,0], [3,10,3]])

    # kernel Laplaciano BORDES
    KERNEL_LAPLACIANO = np.array([ [0,1,0], [1,-4,1], [0,1,0] ])

    ANG_1GRAD = np.pi/180
    
    # Muestra el texto si está en modo DEBUG
    @staticmethod
    def print(*args):
        if (CVUtils.DEBUG_MODE):
            print(*args)

    # Muestra el texto si está en modo DEBUG
    @staticmethod
    def log(*args):
        if (CVUtils.DEBUG_MODE):
            print(*args)
    
    # Muestra el texto si está en modo DEBUG
    @staticmethod
    def debug(*args):
        if (CVUtils.DEBUG_MODE):
            print(*args)


    # Muestra el porcentaje: 0.5 -> 50%
    @staticmethod
    def decimalToPercent(decimal_value):
        if not 0 <= decimal_value:
            raise ValueError("Input value must be between 0 and 1")
        return f"{int(decimal_value * 100)}%"  


    # Convierte color en formato Hex #FFFFFF a RGBA en base 1 (1, 1, 1, 1)
    @staticmethod
    def hexColorToRGBA(sHexcolor):
        # Elimina el '#' si está presente
        if sHexcolor[0] == '#':
            sHexcolor = sHexcolor[1:]

        if len(sHexcolor) == 6:
            # Si no se proporciona el canal alpha, asumimos completamente opaco (255)
            sHexcolor += 'FF'

        # Convierte los componentes hexadecimales a enteros
        r = int(sHexcolor[0:2], 16)
        g = int(sHexcolor[2:4], 16)
        b = int(sHexcolor[4:6], 16)
        a = int(sHexcolor[6:8], 16)

        """
        # Normaliza los valores entre 0 y 1
        r_normalized = r / 255.0
        g_normalized = g / 255.0
        b_normalized = b / 255.0
        a_normalized = a / 255.0
        return [r, g, b, a]
        """
    
        return [r, g, b, a]
    
    #  Convierte Color en formato base 255 (255, 255, 255, 255) a base 1 (1, 1, 1, 1)
    @staticmethod
    def color256ToRGBA(sColor256):
        colors = sColor256.split(',')
        if len(colors) == 3:
            colors.append('255')  # Añade el canal alpha a 1

        """
        for i in range(len(colors)):
            colors[i] = int(colors[i]) / 255.0
        """

        return colors
    
    # Obtiene el color infiriendo su formato (#FFFFFF, (255,255,255), o (1,1,1)) y devuelve en formato opengl (1,1,1,1)
    @staticmethod
    def getColor(color):
        gl_color = color
        if type(color) is str:
            if color[0] == "#":         # String HEX
                gl_color = CVUtils.hexColorToRGBA(color)
            else:                       # String 255,255,255
                gl_color = CVUtils.color256ToRGBA(color)
        else:                           # lista 0..1, 0..1, 0..1
            if len(color) == 3:
                gl_color.append(255)  # Añade el canal alpha a 1

        return gl_color

    #  Lee la imagen y devuelve la img
    @staticmethod
    def readImage(sPath):
        try:
            img = cv.imread(sPath)
            if img is None:
                raise FileNotFoundError(f"No se encontró la imagen en la ruta: {sPath}")
            
            CVUtils.log(f"readImage >>> Imagen {sPath} Leída correctamente:")
            # CVUtils.imageInfo(img)
            return img

        except FileNotFoundError as fnf_error:
            print(f"Error: {fnf_error}")
            raise fnf_error
        except Exception as e:
            print(f"Ocurrió un error al leer la imagen: {e}")
            raise IOError(f"Error al leer la imagen en la ruta: {sPath}") from e
        
    
    #  Lee la imagen y devuelve la img
    @staticmethod
    def writeImage(sPath, img):
        try:
            result = cv.imwrite(sPath, img)
            if not result:
                raise IOError(f"No se pudo guardar la imagen en la ruta: {sPath}")
            CVUtils.log(f"writeImage >>> Imagen {sPath} Grabada correctamente:")
            # CVUtils.imageInfo(img)
            return result
        except Exception as e:
            print(f"Ocurrió un error al guardar la imagen: {e}")
            raise IOError(f"Error al guardar la imagen en la ruta: {sPath}") from e

    
    # Devuelve una imagen GRIS del tamaño indicado con los 3 canales en
    def createImageRGB(width, height, colorValue):
        #img = np.zeros((200,600,3), np.uint8)
        img = np.full((height, width, 3), colorValue, np.uint8)
        #img = np.zeros((height,width,3), np.uint8)
        return img
    
    # Muestra la información de la Imagen
    @staticmethod
    def colorBGR2RGB(img):
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        CVUtils.log(f"colorBGR2RGB >>> Imagen convertida a RGB correctamente:")
        CVUtils.imageInfo(imgRGB)
        return imgRGB
    
    # Muestra la información de la Imagen
    @staticmethod
    def imageInfo(img):
        nCanales = 1 if len(img.shape)<=2 else img.shape[2]
        CVUtils.log(f"imageInfo >>> Imagen: {img.shape[1]}x{img.shape[0]}  x{nCanales} Canales.")

    # Crea una imagen tal cual
    @staticmethod
    def createImg():
        img = np.array ([[90, 90, 0, 0, 0, 90, 90],
                [90, 90, 0, 0, 0, 90, 90],
                [90, 90, 0, 0, 0, 90, 90],
                [90, 90, 0, 0, 0, 90, 90],
                [90, 90, 0, 0, 0, 90, 90],
                [90, 90, 0, 0, 0, 90, 90],
                [90, 90, 0, 0, 0, 90, 90]], dtype=np.uint8)
        return img
    
    # Superpone la matrinz m_insert dentro de la matriz m_main, en la posicion indicada (Si no se indica posición lo coloca en el centro)
    @staticmethod
    def matrixOverlap(m_main, m_insert, posX = None, posY = None):
        return CVUtils.matrixOverlapAlpha(m_main, m_insert, 1.0, posX, posY)
    
    # Superpone la matrinz m_insert dentro de la matriz m_main, en la posicion indicada (Si no se indica posición lo coloca en el centro)
    @staticmethod
    def matrixOverlapAlpha(m_main, m_insert, alpha=1.0, posX=None, posY=None):
        row = posY
        col = posX
        # Si no existe posición, colocarlo en el centro
        if posX is None:
            row = (m_main.shape[0] - m_insert.shape[0]) // 2
            col = (m_main.shape[1] - m_insert.shape[1]) // 2
        # Verificar si la matriz pequeña cabe dentro de la matriz grande en la posición indicada
        if row + m_insert.shape[0] > m_main.shape[0] or col + m_insert.shape[1] > m_main.shape[1]:
            print("La matriz pequeña no cabe en la posición indicada de la matriz grande.")
            return None
        # Copiar la matriz grande para evitar modificar la original
        m_result = m_main.copy()
        # Calcular el valor del canal alfa
        
        maxRow = row + m_insert.shape[0]
        maxCol = col + m_insert.shape[1]
        overlay = m_result[row:maxRow, col:maxCol]
        
        # Para ahorrar cálculos
        if (alpha <= 0):
            pass
        elif (alpha >= 1):
            m_result[row:maxRow, col:maxCol] = m_insert
        else:
            # Aplicar transparencia y superponer la matriz pequeña en la posición indicada de la matriz grande
            m_result[row:maxRow, col:maxCol] = overlay*(1-alpha) + m_insert*alpha

        ###### API:
        ###### m_result[row:maxRow, col:maxCol] = cv.addWeighted(overlay,1-alpha,m_insert,alpha,0)

        CVUtils.log(f">>>>>>>>>           row/col: [{row}..{maxRow},{col}..{maxCol}]  Alpha: {alpha}")
        #m_result = np.clip(m_result, 0, 255)
        return m_result
    
    #  Convierte Color a GRIS en 1 canal
    @staticmethod
    def colorToGray(img):
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)    # Transformación de la imagen a escala de grises
        return img

    #  Convierte Color a GRIS en 3 canales
    @staticmethod
    def colorToGray3(img):
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)    # Transformación de la imagen a escala de grises
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)    # Transformación de la imagen a BGR (con los mismos valores)
        return img
    
    #  Convierte Color a Color en 3 canales
    @staticmethod
    def grayToColor3(img):
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)    # Transformación de la imagen a BGR (con los mismos valores)
        return img
    
    #  FILTER2D: 
    #       img, profundidad de imagen (-1 = igual que original), kernel aplicado
    @staticmethod
    def filter2D(img, kernel, ddepth = -1):
        img = cv.filter2D(img, ddepth, kernel)
        return img
    
    #  BLUR con el kernelSize x kernelSize (Blur en realidad es una Media)
    @staticmethod
    def blur(img, kernelSize):
        img = cv.blur(img, (kernelSize,kernelSize))
        return img
    
    #  BLUR GAUSS con el kernelSize x kernelSize 
    #       img, kernelSize, desviación estandar en X (0 -> autocalculado según kernelSize)
    @staticmethod
    def blurGauss(img, kernelSize, sigmaX = 0):
        img = cv.GaussianBlur(img, (kernelSize,kernelSize), sigmaX)
        return img
    
    #  BLUR MEDIANA con el kernelSize: eliminar ruido de tipo sal y pimienta (filtro estadístico costoso)
    #       img, kernelSize
    @staticmethod
    def blurMedian(img, kernelSize):
        img = cv.medianBlur(img, kernelSize)
        return img
    
    # Filtro de mínimo: selecciona el valor más pequeño de la vecindad. elimina el ruido de sal (píxeles blancos) oscurece la imagen.
    @staticmethod
    def filterMin(img, kernelSize):
        img = cv.erode(img, np.ones((kernelSize, kernelSize), np.uint8))
        return img

    # Filtro de máximo: selecciona el valor más grande de la vecindad. elimina el ruido de pimienta(píxeles negros). aclara la imagen.
    @staticmethod
    def filterMax(img, kernelSize):
        img = cv.dilate(img, np.ones((kernelSize, kernelSize), np.uint8))
        return img
    
    # DownSize: divide la imagen a la mitad, n veces
    @staticmethod
    def downSize(img, niterations = 1):
        for x in range(niterations):
            img = cv.pyrDown(img) 
        return img
    
    # DownSize: aumenta la imagen al doble, n veces
    @staticmethod
    def UpSize(img, niterations = 1):
        for it in range(niterations):
            img = cv.pyrUp(img) 
        return img
    
    # Resize: aumenta/reduce la imagen por factor
    @staticmethod
    def resize(img, factor):
        img_resized = cv.resize(img, (int(img.shape[1] * factor), int(img.shape[0] * factor)) )
        return img_resized


    # zoomImg: realiza un zoom sobre la imagen, centrada si no se indica coord.
    # https://stackoverflow.com/questions/69050464/zoom-into-image-with-opencv
    @staticmethod
    def zoomImg(img, zoom, coord=None, crop=False):
        """
        Simple image zooming without boundary checking.
        Centered at "coord", if given, else the image center.

        img: numpy.ndarray of shape (h,w,:)
        zoom: float
        coord: (float, float)
        """

        #img_resized = cv.resize(img, (int(img.shape[1] * zoom), int(img.shape[0] * zoom)))

        # Translate to zoomed coordinates
        zHeight, zWidth, _ = [ zoom * i for i in img.shape ]
        zoomX, zoomY = zWidth/2, zHeight/2
        
        if not coord is None: 
            zoomX, zoomY = [ zoom*pos for pos in coord ]
        
        zoomImg = cv.resize( img, (0, 0), fx=zoom, fy=zoom)
        if crop:
            zoomImg = zoomImg[ int(round(zoomY - zHeight/zoom * .5)) : int(round(zoomY + zHeight/zoom * .5)),
                int(round(zoomX - zWidth/zoom * .5)) : int(round(zoomX + zWidth/zoom * .5)),
                : ]
        
        return zoomImg
    
    #  ENFOQUE DURO: 
    #       img, profundidad de imagen (-1 = igual que original)
    @staticmethod
    def focusHard(img, niterations = 1):
        for it in range(niterations):
            img = cv.filter2D(img, -1, CVUtils.KERNEL_FOCUS_HARD)
        return img

    #  ENFOQUE SUAVE: 
    #       img, profundidad de imagen (-1 = igual que original)
    @staticmethod
    def focusSoft(img, niterations = 1):
        for it in range(niterations):
            img = cv.filter2D(img, -1, CVUtils.KERNEL_FOCUS_SOFT)
        return img
    

    #  Ecualización: Realza el contraste:   img (necesaria en ESCALA DE GRISES)
    @staticmethod
    def equalizeHist(img):
        img = cv.equalizeHist(img)
        return img

    #  BORDER: Detecta bordes VERTICALES por SOBEL:   img (necesaria en ESCALA DE GRISES)
    @staticmethod
    def sobel_VERT(img):
        img = cv.filter2D(img, -1, CVUtils.KERNEL_SOBEL_EDGE_VERT)
        return img
    
    #  BORDER: Detecta bordes HORIZONTALES por SOBEL:   img (necesaria en ESCALA DE GRISES)
    @staticmethod
    def sobel_HOR(img):
        img = cv.filter2D(img, -1, CVUtils.KERNEL_SOBEL_EDGE_HOR)
        return img
    
    #  BORDER SOBEL FULL: Combina la detección de SOBEL HOR & VERT:   img (necesaria en ESCALA DE GRISES), Invert == IMPAR --> invierte
    @staticmethod
    def sobelFull(img, invert = 0):

        # Normalización de la imagen al intervalo [0,1] y conversión a float64
        imgNorm64 = cv.normalize(img, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_64F)
        imgSobel_x = cv.filter2D(imgNorm64, -1, CVUtils.KERNEL_SOBEL_EDGE_HOR)   
        imgSobel_y = cv.filter2D(imgNorm64, -1, CVUtils.KERNEL_SOBEL_EDGE_VERT)   
        # Cálculo del módulo del gradiente: 
        # img_sobel_x: gradiente en X   /  img_sobel_y: gradiente en Y
        # g: módulo del gradiente (raíz de la suma de los cuadrados)
        imgG = np.sqrt(imgSobel_x**2 + imgSobel_y**2)    # g puede tener valores mayores que 1
        imgG = imgG/np.amax(imgG)     # Normalizar dividiendo por el máximo del gradiente

        # Invertir los niveles de gris del gradiente
        if (invert % 2 != 0):
            # comment: 
            imgG = -1.0*imgG + 1.0

        imgG = cv.normalize(imgG , None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)    # Módulo del gradiente UINT8
        return imgG

    # Transfomración de la profundidad de la imagen a float64
    @staticmethod
    def imgTo64(img):
        img = img.astype('float64')  
        return img
    
    # Normalización al intervalo [0,255] y cambio a tipo uint8
    # Transfomración de la profundidad de la imagen a UINT8
    @staticmethod
    def imgToUINT8(img):
        img = cv.normalize(img , None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
        return img
    
    # Convierte la imagen a formato PhotoImage, para que Tkinter la pueda mostrar
    @staticmethod
    def imgToPhotoImage(img):
        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)    # Convertir la imagen de OpenCV (BGR) a RGB

        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        return img_tk
        
    
    # Convierte la imagen a formato PhotoImage, para que Tkinter la pueda mostrar
    @staticmethod
    def imgToPhotoImageFlat(img):
        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)    # Convertir la imagen de OpenCV (BGR) a RGB
        
        # Convertir la imagen de NumPy array a una cadena en formato PPM
        h, w, _ = img_rgb.shape
        ppm_header = f'P6 {w} {h} 255 '.encode()
        ppm_data = ppm_header + img_rgb.tobytes()
        
        # Crear una imagen de Tkinter a partir de la cadena PPM
        tk_image = PhotoImage(width=w, height=h, data=ppm_data, format='PPM')
        return tk_image

    
    # UMBRALIZACION: Mapa binario de bordes: los que superen el umbra se les asigna 255, el resto 0    img (necesaria en ESCALA DE GRISES)
    @staticmethod
    def threshold(img, limit = 127):
        _, img = cv.threshold(img, limit, 255, cv.THRESH_BINARY)   
        return img
    
    # CANNY: Detección de bordes
    #       img (necesaria en ESCALA DE GRISES)
    #       t1: se elige de forma que incluya todos los bordes que se consideran significativos. Para eliminar bordes no significativos aumentamos t1.
    #       t2: permite descartar bordes que son demasiado acuciados. Para descartar estos bordes reducimos t2.
    @staticmethod
    def canny(img, threshold1, threshold2):
        img = cv.Canny(img, threshold1, threshold2) 
        return img

    # LAPLACIANO: Detección de bordes
    #       img (necesaria en ESCALA DE GRISES)
    @staticmethod
    def laplaciano(img):
        img = cv.normalize(img, None, alpha=0, beta=1, norm_type=cv.NORM_MINMAX, dtype=cv.CV_32F)   # imagen 0/1 32F
        img = cv.filter2D(img, -1, CVUtils.KERNEL_LAPLACIANO) 
        img = cv.normalize(img, None, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)      # imagen 0..255 INT8
        return img
    
    # HoughLines: Detección de líneas
    #       img (necesaria en ESCALA DE GRISES)
    #       rho: resolución del parámetro r, utilizaremos 1.
    #       theta: resolución del parámetro θ en radianes. Utilizaremos 1 grado (pi/180 radianes).
    #       threshold: mínimo número de intersecciones para detectar una línea. Aumentar este parámetro disminuye las líneas detectadas.
    @staticmethod
    def HoughLines(img, theta = np.pi/180, threshold = 140):
        lines = cv.HoughLines(img, 1, theta, threshold)

        imgLines = img.copy()
        imgLines = CVUtils.grayToColor3(imgLines)
        CVUtils.drawLinesHough(imgLines, lines) 

    # HoughLines: Detección de líneas
    #       img (necesaria en ESCALA DE GRISES BINARIA)
    #       rho: resolución del parámetro r, utilizaremos 1.
    #       theta: resolución del parámetro θ en radianes. Utilizaremos 1 grado (pi/180 radianes).
    #       threshold: mínimo número de intersecciones para detectar una línea. Aumentar este parámetro disminuye las líneas detectadas.
    @staticmethod
    def HoughLinesP(img, theta = np.pi/180, threshold = 140, minLineLength = 100, maxLineGap = 10):
        lines = cv.HoughLinesP(img, 1, theta, threshold, minLineLength, maxLineGap)

        imgLines = img.copy()
        imgLines = CVUtils.grayToColor3(imgLines)
        CVUtils.drawLines4(imgLines, lines) 

        return (imgLines, lines)
    

    # findContours_None: Detección de Contornos con Method CHAIN_APPROX_NONE, img (necesaria en ESCALA DE GRISES BINARIA)
    @staticmethod
    def findContours_None(img, minArea = 0, mode = cv.RETR_TREE, method = cv.CHAIN_APPROX_NONE):
        contours, _ =  cv.findContours(img, mode, method)

        if (minArea > 0):
            areaContours = []
            totalArea = img.shape[0]* img.shape[1]    # área total de la imagen
            minAreaContour = totalArea*minArea         # área mínima para ser pintada
            for c in contours:
                c_area = cv.contourArea(c)      # Cálculo del área con la función contourArea
                if (c_area > minAreaContour):
                    areaContours.append(c)
            # end for
            contours = areaContours
        # end if


        CVUtils.log("Se han detectado " + str(len(contours)) + " contornos con method=cv2.CHAIN_APPROX_NONE")

        imgContours = img.copy()
        imgContours = CVUtils.grayToColor3(imgContours)
        cv.drawContours(image=imgContours, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=1, lineType=cv.LINE_AA)

        return (imgContours, contours)
    
    # findContours_None: Detección de Contornos con Method CHAIN_APPROX_SIMPLE, img (necesaria en ESCALA DE GRISES BINARIA)
    @staticmethod
    def findContours_Simple(img, mode = cv.RETR_TREE, method = cv.CHAIN_APPROX_SIMPLE):
        contours, _ =  cv.findContours(img, mode, method)
        CVUtils.log("Se han detectado " + str(len(contours)) + " contornos con method=cv2.CHAIN_APPROX_SIMPLE")

        imgContours = img.copy()
        imgContours = CVUtils.grayToColor3(imgContours)
        cv.drawContours(image=imgContours, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=1, lineType=cv.LINE_AA)

        return (imgContours, contours)




    # Esta funcion dibuja las lineas detectadas por el algoritmo Hough 
    # El último parámetro permite extender las lineas más allá del borde
    @staticmethod
    def drawLinesHough(img, lines, color=(0,0,255), limits=2000):
        if lines is None:
            return
        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + limits*(-b)), int(y0 + limits*(a)))
            pt2 = (int(x0 - limits*(-b)), int(y0 - limits*(a)))
            cv.line(img, pt1, pt2, color, 2, cv.LINE_AA)
            #print(f"rho = {rho}, theta = {theta}, a = {a}, b = {b}, xo = {x0}, yo = {y0}")
            #CVUtils.print(pt1)
            #CVUtils.print(pt2)

    # Esta funcion dibuja las lineas detectadas por el algoritmo HoughP con 4 puntos
    @staticmethod
    def drawLines4(img, lines, color=(0,0,255), limits=2000):
        if lines is not None:
            for line in lines:
                #print(line)
                x1 = line[0,0]
                y1 = line[0,1]
                x2 = line[0,2]
                y2 = line[0,3]
                cv.line(img,(x1,y1),(x2,y2),color,2, cv.LINE_AA)






class CVDraw:
    def __init__(self, pipelineMgr):
        self.pipelineMgr = pipelineMgr

    def drawCircle(self, event, x, y, flags, params = []):

        img = self.pipelineMgr.getCurrentImage()
        cv.circle(img,(x,y),rad,(255,0,0),-1)
        
        if event == cv.EVENT_LBUTTONUP:
            rad = 12
            CVUtils.log(f"Event >> MOUSE_CLICK ({x},{y})")
            img = self.getCurrentImage()
            cv.circle(img,(x,y),rad,(255,0,0),-1)
            self.updateImage(img)

    











"""
    ................................... clase USETUP
"""
class USetup:

    # Leera de un json los defaults
    def __init__(self, filename):
        self.filename = filename
        self.load()

    def load(self):
        self.setup = FileUtils.jsonReadFile(self.filename)

    def getSetup(self, setupField):
        return self.setup.get(setupField, None)
    
    def getKeys(self):
        return self.setup.keys()
    









"""
    ................................... clase FileUtils
"""
# Clase de utilidades de Ficheros (lectura-escritura-...)
class FileUtils:

    @staticmethod
    def jsonReadFile(file_path, relative = True):
        if relative:
            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            file_path = os.path.join(__location__, file_path)
        with open(file_path, 'r', encoding='utf-8') as file:
            #CVUtils.log(f".......leyendo {file_path}")
            json_data = json.load(file)
            return json_data
        
    @staticmethod
    def jsonSaveFile(file_path, object):
        try:
            # Guardar el objeto en el archivo como JSON
            with open(file_path, 'w') as f:
                json.dump(object, f, indent=4)
            CVUtils.debug(f"Objeto guardado en {file_path}")
        except Exception as e:
            CVUtils.debug(f"Error al guardar el archivo: {e}")















