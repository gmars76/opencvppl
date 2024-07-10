import tkinter as tk
from tkinter import ttk, messagebox

from cvUtils import CVUtils
from action import UActionManager



"""
    ................................... clase UViewportManager
"""
class UViewportManager(ttk.Notebook):

    SETUP_VW_MGR_BASE = "viewportManager_base"
            
    # UMenu(self, parent, "panel_tools")
    def __init__(self, parent, openCVPpl,  setupKey):
        super().__init__(parent)
        self.parent = parent
        self.openCVPpl = openCVPpl
        self.pack(expand=True, fill='both')
        
        self.setup = self.openCVPpl.getSetup(setupKey)

        self.tabs = []

        self.bind("<Double-1>", self.on_close_tab)
        self.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def getCurrentViewportId(self):
        return self.index(self.select())
    
    def getCurrentViewport(self):
        try:
            return self.tabs[self.getCurrentViewportId()]
        except Exception as e:
            return None

    def open_image(self, file_path):
        if file_path:
            #img = cv.imread(file_path)
            img = CVUtils.readImage(file_path)
            if img is not None:
                params = {}
                params["file_path"] = file_path
                newViewport = self.add_image(file_path, img)
                newViewport.do_action(UActionManager.ACTION_OPEN, params)


    # Crea un nuevo Viewport para la IMG
    def add_image(self, file_path, img):

        newViewportId = self.index("end")
        newViewport = UViewport(self, self.openCVPpl, file_path, img, UViewport.SETUP_VW_BASE)
        
        self.add(newViewport, text=newViewport.getTitle())
        self.tabs.append(newViewport)
        #self.pack(expand=True, fill='both')

        newViewport.display_image()

        # establece la última pestaña:
        #self.tab_control.select(self.tab_control.index("end")-1)
        self.select(newViewportId)

        return newViewport

    def close_tab(self):
        
        #x, y, widget = event.x, event.y, event.widget
        #viewportId = self.index("@{},{}".format(x, y))
        closeViewportId = self.getCurrentViewportId()
        currentVW = self.getCurrentViewport()

        # Si está modificada...
        if (currentVW.modified):
            response = messagebox.askyesnocancel("Guardar Cambios", "Se realizaron modificaciones en la imagen, ¿Desea grabar los cambios antes de cerrar?")
            if response is None:        # CANCELA
                return
            elif response:              # ACEPTA
                self.openCVPpl.add_action(UActionManager.ACTION_SAVE)

        # Cierra la pestaña
        self.forget(closeViewportId)
        self.tabs.pop(closeViewportId)

        # No se ejecuta: se realiza todo desde aquí
        # self.openCVPpl.add_action(UActionManager.ACTION_CLOSE)

        # Coloca en la última 
        #TODO: debería colocar en la última abierta
        if self.index("end") > 0:
            self.select(self.index("end")-1) 

        self.openCVPpl.panels_update()

    def updateCurrentViewportTitle(self):
        vw_id = self.getCurrentViewportId()
        vw = self.getCurrentViewport()
        self.tab(vw_id, text=vw.getTitle())

    def on_tab_changed(self, event):
        self.openCVPpl.on_tab_changed(event)
        
    def on_close_tab(self, event):
        self.close_tab()


        


"""
    ................................... clase UViewport
"""
class UViewport(ttk.Frame):

    SETUP_VW_BASE = "viewport_base"

    def __init__(self, parent, openCVPpl, file_path, img, setupKey):
        super().__init__(parent)
        self.pack(expand=True, fill='both')

        self.parent = parent
        self.openCVPpl = openCVPpl
        self.setFilePath(file_path)
        self.setup = self.openCVPpl.getSetup(setupKey)
        self.modified = False
        self.actionManager = UActionManager(self)
        self.log_entries = []

        self.zoom = self.setup.get("zoom_ini")

        self.buildUI()

        # La IMAGEN
        # self.source_img = img
        self.img = img.copy()   # Copia de TRABAJO

    # Construye la interfaz 
    def buildUI(self):
        self.canvas = tk.Canvas(self)
        h_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.pack(side="bottom", fill="x")
        v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

    def getTitle(self):
        sMod = "*" if self.modified else ""
        return f"{self.file_name} ({CVUtils.decimalToPercent(self.zoom)}) {sMod}"
    
    def updateTitle(self):
        self.parent.updateCurrentViewportTitle()

    def setFilePath(self, file_path):
        self.file_path = file_path
        self.file_name = file_path.split('/')[-1]

    def display_image(self):
        # Primero aplico zoom y la paso a formato PhotoImage (para tk)
        img_resized = CVUtils.resize(self.img, self.zoom)
        img_tk = CVUtils.imgToPhotoImage(img_resized)


        #(pos_x, pos_y) = self.image_centered_position(self, img_tk)
        (pos_x, pos_y) = (0, 0)

        self.canvas.create_image(pos_x, pos_y, anchor="nw", image=img_tk)
        self.canvas.img_tk = img_tk  # Reference to avoid garbage collection
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    # Calcula la posición centrada de la imagen
    def image_centered_position(self, canvas, img_tk):
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        img_width = img_tk.width()
        img_height = img_tk.height()

        # Calcular la posición centrada
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2

        return (x, y)
    
    # Añade una entrada al log
    def log(self, text):
        self.log_entries.append(text)

    def on_mouse_wheel(self, event):
        if self.img is not None:
            if event.delta > 0:
                self.do_action(UActionManager.ACTION_ZOOM_IN)
            elif event.delta < 0:
                self.do_action(UActionManager.ACTION_ZOOM_OUT)








    """
        Realiza una acción sobre la imagen:
            - ejecuta la acción sobre la imagen
            - guarda en el histórico los pasos
            - modified = true
    """
    def do_action(self, actionName, params = None, updateHistory = True):
        
        actionSetup = UActionManager.get_actionSetup(actionName)

        # Pre_action............

        # Ejecuta la acción............
        match actionName:
            case UActionManager.ACTION_OPEN:
                self.action_open()
            case UActionManager.ACTION_SAVE:
                self.action_save(params)
            case UActionManager.ACTION_ZOOM_IN:
                self.action_zoom_in()
            case UActionManager.ACTION_ZOOM_OUT:
                self.action_zoom_out()

            # Operación AUTOMATICA JSON para el resto
            case _:
                params = self.action_execute(actionName, params)

        # Post_action............
        if actionSetup.get("history"):

            # CREA LA ACCION:
            self.actionManager.add_history_action(actionName, params, updateHistory)

        if actionSetup.get("modify"):
            self.modified=True

        self.updateTitle()
        #CVUtils.debug(f" >>> ACTION {actionName}: PARAMS {params}")
        CVUtils.debug(f" >>> [{self.file_name}] \tACTION {actionName}")
        self.log(f" >>> [{self.file_name}] \tACTION {actionName}")


        

    """
        ..................... OPERACIONES AVANZADAS: AUTOMATICO JSON
    """
    def action_execute(self, actionName, params = None):
        action_setup = UActionManager.SETUP.getSetup(actionName)
        method_name = action_setup.get("method")
        params_info = action_setup.get("params")

        # Extraer los valores iniciales de los parámetros
        paramValues = []
        for param_name, param_details in params_info.items():
            paramValue = None
            # Si es el param "img" lo establezco
            if param_name == "img":
                paramValue = self.img
            else:
                # Si ya esta establecido lo dejo
                if param_name in params and params[param_name]:
                    paramValue = params[param_name]
                else:
                    # Sino, pongo el initValue
                    if "initValue" in param_details:
                        paramValue = param_details["initValue"]
            params[param_name] = paramValue
            paramValues.append(paramValue)

        # Llamar al método estático
        method = getattr(CVUtils, method_name)
        self.img = method(*paramValues)
        # Refresco la imagen
        self.display_image()
        
        # Devuelve los parametros reales ejecutados
        return params
               
        
    """
        ..................... RE-EJECUTA LA ÚLTIMA ACTION CON EL PARAM_KEY modificado (se ha modificado un parámetro)
    """
    def action_redo(self):
        updateHistory = False
        action = self.actionManager.getCurrentAction()

        self.actionManager.set_action_previous()
        self.do_action(action.actionName, action.actionParams, updateHistory)
        self.openCVPpl.panels_update()


    """
        ..................... OPERACIONES BÁSICAS
    """
    def action_open(self):
        # No hace nada, desde el viewportManager se crea el newViewport 
        pass

    def action_save(self, params):
        if "file_path" in params and params["file_path"]:
            save_path = params["file_path"]
            #cv.imwrite(save_path, image_data)
            CVUtils.writeImage(save_path, self.img)
            self.setFilePath(save_path)
            self.modified = False
            messagebox.showinfo("Imagen Guardada", "Imagen guardada con éxito!")

    def action_zoom_in(self):
        self.zoom *= 1.2
        self.display_image()

    def action_zoom_out(self):
        self.zoom /= 1.2
        self.display_image()

    def set_action_previous(self):
        self.actionManager.set_action_previous()
        self.openCVPpl.panels_update()
    def set_action_next(self):
        self.actionManager.set_action_next()
        self.openCVPpl.panels_update()
        

    # Pipeline OPEN
    def action_pipeline_open(self, file_path):
        pipeline_actions = self.actionManager.open_pipeline(file_path)
        print(pipeline_actions)

        for action in pipeline_actions:
            self.do_action(action["actionName"], action["actionParams"])

        self.openCVPpl.panels_update()


    # Pipeline SAVE
    def action_pipeline_save(self, file_path):
        self.actionManager.save_pipeline(file_path)

