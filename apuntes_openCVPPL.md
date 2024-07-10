
## INFO GUI:
    https://docs.opencv.org/4.x/dc/d46/group__highgui__qt.html


## TODO:
- [ok]: Panel Herramientas
- [ok]: verificar Zoom
- [ok]: Rueda ratón Zoom
- [ok]: Eliminar referencias import cv2 as cv
- [ok]: Panel parametros
- [ok]: Al abrir imagen sitúa en el tab
- [ok]: ERROR: "Save" Falla
- [ok]: cerrar pestaña doble click
- [ok]: que funcione la herramienta B&W
- [ok]: ERROR: cierro tab 2, y al cerrar tab 3 falla
- [ok]: Que al grabar precargue el filepath del archivo
- [ok]: Descomponer el grabar en viewportMgr.save_image
- [ok]: Error paneles no se ven
- [ok]: UViewportManager -> UViewport's
- [ok]: Wheel -> al cambiar el zoom revisar el título
- [ok]: ActionManager funcionando
- [ok]: ERROR: al salvar con otro nombre no cambia el título de la pestaña
- [ok]: Primer Pipeline
- [ok]: Pipeline lee parametros y descripciones de JSON
- [ok]: Error: al arrastrar un panel desde el título no funciona
- [ok]: Error: el modified no funciona, siempre trata de guardar
- [ok]: Error: al cerrar la última pestaña
- [ok]: Mostrar Actions en el panel
- [ok]: ERROR: al hacer click sobre un panel hace parpadeo: SOLUCION: opencvppl.panels_hide desactivado
- [--]: Mejora: mostrar la imagen centrada si es mas pequeña que el viewport
- [ok]: Mejora: paneles en porcentaje de la pantalla: a 50 de los lados
- [ok]: Comprobar COLORES en el HIST
- [ok]: Parametros explicados en JSON --> action_text
- [Ok]: Al cambiar el historico cambia la imagen
- [ok]: Al cambiar de tab no se cambia el action_text
- [ok]: MEJORA: el actions.JSON puede procesarse automaticamente: con un campo "método automático"=True --> se llama a la función de CVUTILS a partir del JSON:
        # Llamar al método estático utilizando getattr
        method = getattr(MyClass, method_name)
        method()  # Esto llamará a MyClass.my_static_method
- [ok]: ERROR: cambiar el history actions falla al situarse en el 0
- [ok]: MACROS: grabar macros en un JSON: { "macro_name_1": [ "action_colorToGray", "action_blurGauss", "action_blurMedian" ], "macro_name_2": [] } 
    >> incluso incluyendo los valores de los parámetros: "action_colorToGray": { "img", 4, "aaa" }
- [ok]: TECLADO: parametros por teclado, ATRAS-ADELANTE en el pipeline (AvancePagina-RetrocederPagina?)
- [--]: TECLADO: ESPACIO  para realizar un PAN por la imagen
- [--]: MEJORA: en setupActions podemos añadir un campo "section" o "style" que indique la sección o el estilo del botón (así agrupamos los botones inocuos y los de open-save)
- [ok]: TODO: en el viewport.action_execute() llegan los params, hay que almacenarlos --> Teclado --> modifica param y se ejecuta
- [ok]: ERROR: error NoneType al arrancar
- [ok]: TODO: teclado con teclas del currentAction
- [ok]: TODO: manejar la pila de acciones con modificaciones: si modifica una tecla, la pila persiste, pero debe actualizarse RE-EJECUTANDO los nuevos parametros
- [ok]: TODO: manejar pila de acciones: si está a la mitad y se pulsa una acción del toolbar se borran las acciones posteriores.
- [--]: MEJORA: permitir varios PanelTools: desde el menú se puede seleccionar cual se quiere mostrar
- [ok]: TODO: Menu Pipeline/Abrir Pipeline/Salvar (al salvar no salva open_file save_file)
- [ok]: TODO: Cargar Pipeline --> añade los actions al pipeline actual. al final pregunta: "desea procesar el pipeline?" y lo ejecuta.
- [--]: TODO: controlar errores de parametros min-max en CvUtils
- [ok]: TODO: botones de history con titulo de actionname
- [--]: TODO: menú Ayuda: muestra un panel con un texto explicativo -> teclas especiales y demás
- [ok]: ERROR: abre 2 veces un pipeline falla (Canales en B&N)
- [ok]: ERROR: redo de un paso anterior borra los superiores (debe respetar a los posteriores en la lista)
- [ok]: ERROR: al cerrar una imagen sus acciones permanecen
- [ok]: MEJORA: Panel Info: text+scroll: muestra acciones, errores, excepciones....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....
- [--]: ....


# Tkinter TEXT:
https://tkdocs.com/tutorial/text.html#basics


## Problema:
The library is compiled without QT support in function 'cv::createButton'

https://wiki.qt.io/How_to_setup_Qt_and_openCV_on_Windows



### tkinter tk
https://www.youtube.com/watch?v=jqRHhWjKDD8
Dimas:
    https://www.youtube.com/watch?v=MpkTYMzhV0A
    https://www.youtube.com/watch?v=_LiX8Bd2Jq0

tabs:
https://stackoverflow.com/questions/67543794/how-do-i-create-tabs-in-tkinter-dynamically


# TESTs:
- **test_tk_old.py** --> funcionan los eventos, el zoom, y el panel
- **test_tk_tab.py** --> funcionan las pestañas, falta el X de la pestaña

- CloseTab: 
    - https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook
    - https://wiki.tcl-lang.org/page/ttk%3Anotebook+help



# ejemplo poo tkinter
    https://www.youtube.com/watch?v=3NwkwLGW4OQ