import cv2 as cv
import numpy as np

from cvUtils import CVUtils



"""
# Clase CVPipeline: se le van añadiendo procesos y va pasando de uno a otro con "ESPACIO"/"RETROCESO", y permite ir variando parametros    
Se trata de crear un pipeline e ir añadiendole procesos/fases:
    pipe = CVPipeline("Prueba Laplaciano", "images/cultivo.jpg")
    pipe.addProcess( "Down Size", CVUtils.downSize, [(2,"s", 1)] )
    pipe.addProcess( "A Gris", CVUtils.colorToGray,  [] )
    pipe.addProcess( "Blur Gauss", CVUtils.blurGauss, [(3,"k", 2)] )
    pipe.execute()
A cada proceso que añades le indicas sus parametros:
	(valorInicial, TECLA, incremento): cada vez que pulses la tecla en esa fase se incrementa el parámetro (si pulsas mayusculas se decrementa)
Cuando le das a ejecutar ira pasando de fase a fase (todo está en el titulo de la ventana)
	- ESPACIO para avanzar fase
	- BACKSPACE para retroceder fase
	- ESCAPE termina en cualquier fase
"""
class CVPipeline:
    KEYS_NEXT = ord(" ")

    WINDOW_NAME = "opencvPPL"

    def __init__(self, name, sourceImagePath):
        self.name = name
        self.process = []
        self.imgBuffer = []

        self.initProcess(sourceImagePath)

    # Inicia el pipeline con la imagen
    def initProcess(self, sourceImagePath):
        self.process = []
        self.imgBuffer = []

        self.color = "#FF0000"
        self.bgColor = "#555555"

        self.addProcess( "Imagen Original", CVUtils.readImage, [(sourceImagePath,"P", "")], False )

    def getWindowID(self): return CVPipeline.WINDOW_NAME
    def getCurrentImage(self): return self.imgBuffer[len(self.imgBuffer)-1]
    def updateImage(self, img): cv.imshow(self.getWindowID(), img)
    def getColor(self): return self.color
    def getBgColor(self): return self.bgColor


    # Añade un proceso a la cola de procesos:
    #   - name:         aparecerá en la ventana
    #   - function:     función a ejecutar
    #   - params:       array de parámetros para pasar a la función en vector: (paramValue, KEY, keyIncrement) [ (), (), ... ]
    def addProcess(self, name, function, params, imgProcess = True):
        self.process.append( CVProcess(name, function, params, imgProcess) )


    # mouse callback function
    def drawCircle(self, event, x, y, flags, params = []):
        if event == cv.EVENT_LBUTTONUP:
            rad = 12
            CVUtils.log(f"Event >> MOUSE_CLICK ({x},{y})")
            img = self.getCurrentImage()
            cv.circle(img,(x,y),rad,(255,0,0),-1)
            self.updateImage(img)

    def execute(self):

        currentProc = 0
        running = True

        while (running):

            if (currentProc < len(self.process)):

                proc = self.process[currentProc]
                CVUtils.log(f">>> {self.name} [{str(currentProc)}]: {proc.name}")
                proc.printParams()

                # Leo los args (y añado la última imagen si procede)
                args = proc.getProcessArgs()
                if (proc.imgProcess):
                    lastImg = self.imgBuffer[currentProc-1]
                    args.insert(0, lastImg)

                # Ejecuto la función del PROCESO
                result = proc.function( *args )

                # Añado el resultado al buffer en su posición
                if (currentProc < len(self.imgBuffer)):
                    self.imgBuffer[currentProc] = result
                else:
                    self.imgBuffer.append(result)

                # Si el resultado es compuesto obtengo la img (la primera del resultado)
                img = result
                if isinstance(result, tuple):
                    img = result[0]
                wTitle = f"{self.name} :: Fase {currentProc}     --> " +proc.getTitle()
                cv.imshow(self.getWindowID(), img)
                
                cv.setWindowTitle(self.getWindowID(), wTitle)

                # Establece el escuchador de eventos
                cv.setMouseCallback(self.getWindowID(),self.drawCircle)
                
                key = cv.waitKey()
                CVUtils.log(key)
                # KEY PARAM
                for param in proc.params:
                    if (key == param.keyPlus):
                        param.value += param.increment
                    elif (key == param.keyMinus):
                        param.value -= param.increment

                # FASE SIGUIENTE / ANTERIOR
                if (key == CVUtils.KEY_SPACE):
                    currentProc += 1
                elif (key == CVUtils.KEY_BACKSPACE):
                    currentProc -= 1
                    if (currentProc < 0):
                        currentProc = 0
                elif (key == CVUtils.KEY_ESCAPE):
                    running = False

                elif (key == ord("C")):
                    img = np.zeros((200,600,3), np.uint8)
                    cv.imshow(self.getWindowID(), img)
                
                #cv.destroyAllWindows()
            else:
                running = False
        # end while
        return self.imgBuffer
            



        


            


    
"""
    ................................... clase CVProcess
"""
class CVProcess:
    def __init__(self, name, function, params, imgProcess = True):
        self.name = name
        self.function = function
        self.params = []
        self.imgProcess = imgProcess
        for param in params:
            self.params.append( CVParam(*param) )
    
    def getProcessArgs(self):
        args = []
        for param in self.params:
            args.append(param.value)
        return args
    
    def printParams(self):
        CVUtils.log("Params:")
        for param in self.params:
            param.print()

    def getTitle(self):
        ps = " ["
        for param in self.params:
            ps += f" {param.getTitle()} --"
        ps += " ]"
        title = f"{self.name}{ps}"
        return title
    


"""
    ................................... clase CVParam --> Procesos
"""
class CVParam:
    def __init__(self, value, key="", increment=0):
        self.value = value
        lowerKey = str.lower(key)
        self.keyPlus = ord(lowerKey)
        self.keyMinus = ord(lowerKey)-32
        self.increment = increment
    def print(self):
        CVUtils.log(f"[ {self.getTitle()} ]")
    def getTitle(self):
        return f"{chr(self.keyPlus)}/{chr(self.keyMinus)}: {self.value}"
    


