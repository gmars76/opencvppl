import tkinter as tk
from tkinter import filedialog, messagebox

from cvUtils import USetup
from action import UActionManager
from panel import UMenu, UPanel, UPanelActions, UPanelTools, UPanelInfo
from viewport import UViewportManager

class OpenCVPPL(tk.Tk):

    PAN_TOOLS = "panel_tools"
    PAN_ACTIONS = "panel_actions"
    PAN_INFO = "panel_info"
    JSON_SETUP = "opencvPPL.setup.json"

    KEY_BACKSPACE = 'BackSpace'
    KEY_TAB = 'Tab'
    KEY_RETURN = 'Return'
    KEY_ESCAPE = 'Escape'
    KEY_UP = 'Up'
    KEY_DOWN = 'Down'
    KEY_LEFT = 'Left'
    KEY_RIGHT = 'Right'
    KEY_SHIFT_L = 'Shift_L'
    KEY_SHIFT_R = 'Shift_R'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Configuración
        self.setup = USetup(OpenCVPPL.JSON_SETUP)


        self.title(self.setup.getSetup("appTitle"))
        self.state('zoomed')
        self.container = tk.Frame(self)
        self.container.pack(
            side = tk.TOP,
            fill = tk.BOTH,
            expand = True
        )
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.parent = self

        sFont = self.setup.getSetup("font_text")
        self.font_text = ( sFont.get("name"), sFont.get("size"), sFont.get("weight") )
        #self.option_add("*Text.Font", font_text)

        # Manejador de los tabs
        self.viewportMgr = UViewportManager(self.container, self, UViewportManager.SETUP_VW_MGR_BASE)

        # Menu
        self.menu = UMenu(self, "mnu_main")

        # ................ Paneles
        self.panels = {}
        self.panels[OpenCVPPL.PAN_TOOLS] = UPanelTools(self, OpenCVPPL.PAN_TOOLS)
        self.panels[OpenCVPPL.PAN_ACTIONS] = UPanelActions(self, OpenCVPPL.PAN_ACTIONS)
        self.panels[OpenCVPPL.PAN_INFO] = UPanelInfo(self, OpenCVPPL.PAN_INFO)
        self.panels_visible = True

        # Bind focus para que se vean todos los paneles
        self.bind("<FocusIn>", self.panels_show)
        #self.bind("<FocusOut>", self.panels_hide)

        #self.bind_all('<KeyPress>', self.on_key_release)
        self.bind_all('<KeyRelease>', self.on_key_release)
        
        # Bind the mouse wheel for zooming
        # self.canvas.bind("<MouseWheel>", self.mouse_zoom)

    def getSetup(self, setupField):
        return self.setup.getSetup(setupField)
    
    def getViewportManager(self):
        return self.viewportMgr
    
    def panels_show(self, event=None):
        if self.panels_visible:
            for panel in self.panels.values():
                panel.show()

    def panels_hide(self, event=None):
        for panel in self.panels.values():
            panel.hide()

    # Realiza la acción sobre la imagen y refresca los paneles correspondientes
    def add_action(self, actionName, params={}):

        try:
            # Acción inicial: crea el viewport
            if actionName == UActionManager.ACTION_OPEN:
                file_path = params.get("file_path")     # Devuelve None si no existe
                if not file_path:
                    file_path = self.action_open_image()
                params["file_path"] = file_path
                self.viewportMgr.open_image(params["file_path"])
            
            # Acción final: cierra el viewport
            elif actionName == UActionManager.ACTION_CLOSE:
                    self.action_close_tab()

            # Acciones sin history (abrir/salvar pipeline)
            elif actionName == UActionManager.ACTION_PIPELINE_OPEN:
                self.action_pipeline_open(params)
            elif actionName == UActionManager.ACTION_PIPELINE_SAVE:
                self.action_pipeline_save(params)

            # Acciones Generales con history (--> )
            else:
                viewport = self.viewportMgr.getCurrentViewport()
                if viewport is not None:
                    
                    if actionName == UActionManager.ACTION_SAVE:
                        file_path = params.get("file_path")     # Devuelve None si no existe
                        if not file_path:
                            file_path = self.action_save_image(viewport)
                        params["file_path"] = file_path
                    
                    # DO_ACTION: registra en el history el action
                    viewport.do_action(actionName, params)
                else:
                    messagebox.showinfo("No hay Imagen", "No existe imagen sobre la que operar")

            #TODO: refrescar los paneles de info e histórico
            self.panels_update()

        except FileNotFoundError:
            print("ERROR: La imagen no se encontró en la ruta especificada.")
        except IOError:
            print("ERROR: Ocurrió un error al guardar la imagen.")
        except Exception as e:
            print(f"Ocurrió un error realizar la acción: {e}")

    
    # Atajo para abrir nuevo fichero
    def file_open(self, file_path):
        params = { "file_path": file_path }
        self.add_action(UActionManager.ACTION_OPEN, params)

    # Atajo para salvar el fichero actual
    def file_save(self):
        currentVW = self.viewportMgr.getCurrentViewport()
        params = { "file_path": currentVW.file_path }
        self.add_action(UActionManager.ACTION_SAVE, params)

    
    # Si el file_path está vacío lo pide
    def action_open_image(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.tiff")])
        return file_path

    # solicita el file_path para guardar el archivo (precarga el actual)
    def action_save_image(self, viewport):
        initial_dir = viewport.file_path.rsplit('/', 1)[0]
        initial_file = viewport.file_path.rsplit('/', 1)[1]
        default_extension = "." + initial_file.rsplit('.', 1)[1]
        save_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=default_extension,
            title="Guardar como",
            filetypes=(("image files", "*.jpg *.png *.gif *.bmp"),("All files", "*.*"))
        )
        return save_path

    # No se ejecuta: se cierra directamente en el viewportManager
    def action_close_tab(self):
        viewport = self.viewportMgr.getCurrentViewport()
        if viewport is not None:
            self.viewportMgr.close_tab()


    def action_pipeline_open(self, params):
        viewport = self.viewportMgr.getCurrentViewport()
        if viewport is not None:
            # TODO: Preguntar "Esto es lo que va a Grabar, ok?"
            file_path = params.get("file_path")     # Devuelve None si no existe
            if not file_path:
                file_path = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
            params["file_path"] = file_path
            viewport.action_pipeline_open(file_path)
    
    def action_pipeline_save(self, params):
        viewport = self.viewportMgr.getCurrentViewport()
        if viewport is not None:
            file_path = params.get("file_path")     # Devuelve None si no existe
            if not file_path:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json"
                    , filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")] )
            params["file_path"] = file_path
            viewport.action_pipeline_save(file_path)



    def alert(self, title, text, exception=None):
        messagebox.showinfo(title, text)


    def on_tab_changed(self, event):
        self.panels_update()

    # Actualiza los paneles:
    def panels_update(self):
        currentVW = self.viewportMgr.getCurrentViewport()
        self.panels[OpenCVPPL.PAN_ACTIONS].updateActions(currentVW)
        self.panels[OpenCVPPL.PAN_INFO].updateLog(currentVW.log_entries)


    # Control de teclado:
    def on_key_release(self, event):
        keyPressed = event.keysym
        variableKeys = None
        viewport = self.viewportMgr.getCurrentViewport()
        if viewport:
            action = viewport.actionManager.getCurrentAction()
            variableKeys = UActionManager.get_actionVariableKeys(action.actionName)
            variableKeys = variableKeys + [paramKey.upper() for paramKey in variableKeys]    # Añade las mayúsculas
            #print(f"TECLA {keyPressed} {action.actionName} VARIABLE:{variableKeys}")

        if keyPressed == OpenCVPPL.KEY_ESCAPE:
            self.destroy()  # Cierra la aplicación

        elif keyPressed in [ OpenCVPPL.KEY_SHIFT_L, OpenCVPPL.KEY_SHIFT_R ]:
            pass

        elif keyPressed == OpenCVPPL.KEY_TAB:
            if self.panels_visible:
                self.panels_visible = False
                self.panels_hide()
            else:
                self.panels_visible = True
                self.panels_show()

        
        elif keyPressed == OpenCVPPL.KEY_DOWN:
            viewport.set_action_previous()
        elif keyPressed == OpenCVPPL.KEY_UP:
            viewport.set_action_next()

        # Si ha pulsado una de las teclas parametros del Action:
        elif keyPressed in variableKeys:
            action = viewport.actionManager.getCurrentAction()
            action.updateParamValue(keyPressed)
            viewport.action_redo()




            
            





    




