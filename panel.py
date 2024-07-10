import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from action import UActionManager


"""
    ................................... clase UMENU
"""
class UMenu(tk.Menu):
    # UMenu(self, parent, "panel_tools")
    def __init__(self, parent, setupKey):
        super().__init__(parent)
        self.parent = parent
        self.parent.config(menu=self)
        self.create_menu()
    
    def create_menu(self):
        file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command( label="Abrir", command=lambda:self.parent.add_action(UActionManager.ACTION_OPEN, {}) )
        file_menu.add_command( label="Guardar", command=lambda:self.parent.add_action(UActionManager.ACTION_SAVE, {}) )
        file_menu.add_command( label="Cerrar", command=lambda:self.parent.add_action(UActionManager.ACTION_CLOSE, {}) )

        file_pipelines = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Pipeline", menu=file_pipelines)
        file_pipelines.add_command( label="Abrir", command=lambda:self.parent.add_action(UActionManager.ACTION_PIPELINE_OPEN, {}) )
        file_pipelines.add_command( label="Guardar", command=lambda:self.parent.add_action(UActionManager.ACTION_PIPELINE_SAVE, {}) )





"""
    ................................... clase UFRAMESCROLLABLE
"""
class UFrameScrollable(ttk.Frame):

    def __init__(self, parent, vertical=True, bgcolor="#777777"):
        canvas = tk.Canvas(parent)
        super().__init__(canvas)
        
        if vertical:
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill="y")
            canvas.configure(yscrollcommand=scrollbar.set)
        else:
            scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
            scrollbar.pack(side=tk.TOP, fill="x")
            canvas.configure(xscrollcommand=scrollbar.set)

        super().__init__(canvas)
        self.bind( "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")) )

        canvas.create_window((0, 0), window=self, anchor="nw")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.config(bg=bgcolor)

        # Función para el desplazamiento con la rueda del ratón
        def on_mouse_wheel(event):
            if vertical:
                canvas.yview_scroll(int(-1*(event.delta/50)), "units")
            else: 
                canvas.xview_scroll(int(-1*(event.delta/50)), "units")
        canvas.bind("<MouseWheel>", on_mouse_wheel)

    # Borra todos los elementos del frame
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()



"""
    ................................... clase UText
"""
class UText(scrolledtext.ScrolledText):

    FONT_NORMAL = "normal"
    FONT_BOLD = "bold"
    FONT_ITALIC = "italic"
    FONT_KEY = "key"
    FONT_VALUE = "value"
    FONT_H1 = "h1"
    FONT_TITLE = "title"

    def __init__(self, parent, font_base, editable=True, height=10, bg_color="#b2b2b2", fg_color="#333333"):
        super().__init__(parent)

        self.font_base = font_base
        self.font_bold = (self.font_base[0], self.font_base[1], "bold")
        self.font_italic = (self.font_base[0], self.font_base[1], "italic")
        
        self.config(
            wrap="word"
            , height=height
            , bg=bg_color
            , fg=fg_color
            , font=font_base
        )
        self.editable = editable
        if not self.editable:
            self.config(state=tk.DISABLED)  # Deshabilitar edición

        self.tag_configure(UText.FONT_NORMAL, font=self.font_base)
        self.tag_configure(UText.FONT_BOLD, font=self.font_bold)
        self.tag_configure(UText.FONT_ITALIC, font=self.font_italic)
        self.tag_configure(UText.FONT_KEY, background="#B53471", foreground="#ffffff", font=('Helvetica', 12, 'bold'))
        self.tag_configure(UText.FONT_VALUE, background="#1B1464", foreground="#ffffff", font=('Helvetica', 10, 'bold'))

    # Actualiza el text
    def setText(self, text, font=None, clear=False):
        padding = ""
        font = UText.FONT_NORMAL if font is None else font
        if font in [UText.FONT_KEY, UText.FONT_VALUE]:
            padding = "  "
        self.config(state=tk.NORMAL)
        if clear:
            self.delete("1.0", tk.END)
        self.insert(tk.END, padding + text + padding, font)
        if not self.editable:
            self.config(state=tk.DISABLED)



"""
    ................................... clase UHISTORYBUTTON
"""
class UHistoryButton(tk.Button):
    def __init__(self, parent, index, action, modified=False):
        super().__init__(parent)
        
        self.parent = parent
        self.index = index
        self.action = action

        # Configura el botón
        modified_text = "*" if modified else ""
        button_text = f"{index}: {UActionManager.get_actionTitle(action.actionName)} {modified_text}"
        self.config(text=button_text, relief=tk.FLAT, anchor="nw", bg="#bbbbbb", width=200)
        self.pack(pady=0, padx=2, fill=tk.X)















"""
    ................................... clase UPANEL
"""
class UPanel(tk.Toplevel):

    SETUP_BASE_KEY = "panel_base"

    def __init__(self, parent, setupKey,):
        super().__init__(parent)
        self.parent = parent
        self.setup = self.parent.getSetup(setupKey)
        setup = self.setup
        setupBase = self.parent.getSetup(UPanel.SETUP_BASE_KEY)

        # Configura panel
        self.configure(borderwidth=setupBase.get("borderwidth"), bg=setupBase.get("bgcolor"))
        self.geometry(setup.get("geometry"))
        self.overrideredirect(True)
        self.resizable(True, True)

        # Crea panel title
        self.panel_title = tk.Frame(self, bg=setupBase.get("title_bgcolor"))
        self.panel_title.pack(fill=tk.X)
        self.panel_title.bind("<ButtonPress-1>", self.move_start)
        self.panel_title.bind("<ButtonRelease-1>", self.move_stop)
        self.panel_title.bind("<B1-Motion>", self.move_on)

        self.title_label = tk.Label(self.panel_title, text=setup.get("title"), bg=setupBase.get("title_bgcolor"), fg='white')
        self.title_label.pack(side=tk.LEFT, padx=5)
        self.title_label.bind("<ButtonPress-1>", self.move_start)
        self.title_label.bind("<ButtonRelease-1>", self.move_stop)
        self.title_label.bind("<B1-Motion>", self.move_on)

        # Crea sección principal
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Lo mueve por defecto a la derecha:
        self.move_to_edge("right", 20)

    def show(self):
        #print(f"Muestra {self.title_label['text']}")
        self.deiconify()

    def hide(self):
        self.withdraw()

    # Mueve el panel a la distancia distance del borde de la pantalla
    def move_to_edge(self, edge="right", distance=20):
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        # Obtener dimensiones de la ventana
        self.update_idletasks()  # Asegurarse de que la geometría esté actualizada
        panel_width = self.winfo_width()
        panel_height = self.winfo_height()
        panel_y = self.winfo_y()

        # Calcular nueva posición
        if edge == "left":
            panel_x = distance
        elif edge == "right":
            panel_x = screen_width - panel_width - distance
        else:
            raise ValueError("El valor de 'edge' debe ser 'left' o 'right'")

        # Mover la ventana
        self.geometry(f"{panel_width}x{panel_height}+{panel_x}+{panel_y}")

    def move_start(self, event):
        self.pos_x = event.x
        self.pos_y = event.y

    def move_stop(self, event):
        self.pos_x = None
        self.pos_y = None

    def move_on(self, event):
        x = self.winfo_x() + event.x - self.pos_x
        y = self.winfo_y() + event.y - self.pos_y
        self.geometry(f"+{x}+{y}")








"""
    ................................... clase UPANELTOOLS
"""
class UPanelTools(UPanel):

    def __init__(self, parent, setupKey):
        super().__init__(parent, setupKey)

        self.buttons = []
        self.create_action_buttons()

        self.move_to_edge("left", 20)

    # Crea los botones de action de Tools según UActionManager.get_available_actions()
    def create_action_buttons(self):
        self.buttons = []
        available_actions = UActionManager.get_available_actions()
        
        for i, av_action in enumerate(available_actions):
            self.add_button(av_action["text"], av_action["key"])
        self.pack_buttons()

    def add_button(self, text, actionName):
        self.buttons.append( tk.Button(self.main_frame, text=text, command=lambda:self.parent.add_action(actionName, {})) )


    def pack_buttons(self):
        setup = self.setup
        for i, button in enumerate(self.buttons):
            if i == 0:
                 # Margen de X píxeles arriba y Y píxeles abajo para el primer botón
                button.pack(fill='x', padx=setup.get("btns_padx"), pady=(setup.get("btns_padx"), setup.get("btns_pady"))) 
            else:
                # Empaqueta los demás botones con padding uniforme
                button.pack(fill='x', padx=setup.get("btns_padx"), pady=setup.get("btns_pady"))  











"""
    ................................... clase UPANELACTIONS
"""
class UPanelActions(UPanel):

    def __init__(self, parent, setupKey):
        super().__init__(parent, setupKey)

        self.viewport = None

        # Crear marco principal con grid
        self.container = tk.Frame(self.main_frame)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.container.rowconfigure(0, weight=1)
        self.container.rowconfigure(1, weight=2)
        self.container.columnconfigure(0, weight=1)

        # Crear sección SUPERIOR con texto explicativo................................
        self.frame_top = tk.Frame(self.container)
        self.frame_top.grid(row=0, column=0, sticky="nsew")

        #self.action_text = UText(self.frame_top, wrap="word", height=10, bg=bg_color, font=self.parent.font_text)
        self.action_text = UText(self.frame_top, self.parent.font_text, False, 
                                 self.setup.get("text_height"), self.setup.get("text_bg_color"), self.setup.get("text_fg_color"))
        self.action_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Crear sección INFERIOR con histórico................................
        self.frame_bottom = tk.Frame(self.container)
        self.frame_bottom.grid(row=1, column=0, sticky="nsew")
        self.action_hist = UFrameScrollable(self.frame_bottom)

        """
        # Añadir botones a la sección inferior
        for i in range(20, 0, -1):
            button_text = f"{i}: ActionName"
            button = tk.Button(self.action_hist, text=button_text, command=lambda bt=button_text: self.on_historyButton_click(bt), relief=tk.FLAT)
            button.config(relief="flat", highlightthickness=2, highlightbackground="black", background="red")
            button.pack(pady=0, padx=2, fill=tk.X)
        """
    
    # Borra los paneles
    def clear(self):
        self.action_text.setText("", UText.FONT_NORMAL, clear=True)
        self.action_hist.clear()

    # Refresca los datos del panel según el viewport
    def updateActions(self, viewport):
        if viewport:
            self.viewport = viewport
            actionMgr = viewport.actionManager
            actions = actionMgr.actions
            currentAction = actionMgr.getCurrentAction()
            last_action = actionMgr.last_action

            # PARTE SUPERIOR: TEXTO de la acción
            if currentAction:
                actionSetup = UActionManager.get_actionSetup(currentAction.actionName)
                text = f"Action {currentAction.actionName}\n\tParámetros: {currentAction.actionParams}"
                #self.udpateActionText(text)
                self.action_text.setText(f"Action: ", UText.FONT_BOLD, clear=True)
                self.action_text.setText(f"{currentAction.actionName}\n", UText.FONT_BOLD)
                self.action_text.setText(f"Descripción:\n", UText.FONT_BOLD)
                self.action_text.setText(f"{actionSetup.get('description')}\n", UText.FONT_NORMAL)
                self.action_text.setText(f"Params:\n", UText.FONT_BOLD)
                params = actionSetup.get('params')
                for paramKey in params.keys():
                    param = params.get(paramKey)
                    paramValue = currentAction.actionParams[paramKey]
                    #print(paramKey + ":   ", param)
                    if param.get("variable"):
                        self.action_text.setText("  ")
                        self.action_text.setText(f"{param.get('key')}", UText.FONT_KEY)
                        self.action_text.setText(f"{paramValue}", UText.FONT_VALUE)
                        self.action_text.setText(f":{param.get('description')}\n", UText.FONT_NORMAL)
                #self.action_text.setText(f"\t{actionSetup.get('params')}\n", UText.FONT_NORMAL)


            # PARTE INFERIOR: PANEL DE BOTONES HISTORICO    
            self.action_hist.clear()
            fg_color = self.setup.get("hist_fg_color")
            for index in range(len(actions)-1, -1, -1):
                bg_color = self.get_history_bg_color(index, last_action)
                button = UHistoryButton(self.action_hist, index, actions[index], actions[index].modified)
                button.config(
                    fg=fg_color
                    , bg=bg_color
                    , command=lambda b=button: self.on_historyButton_click(b)
                )
        else:
            self.clear()
            
    # Pulsa en un botón del histórico
    def on_historyButton_click(self, button):
        self.set_history_index(button.index)
        


    def get_history_bg_color(self, index, last_action):
        bg_color = self.setup.get("hist_ON_bg_color")
        if index == last_action:
            bg_color = self.setup.get("hist_CURR_bg_color")
        if index > last_action:
            bg_color = self.setup.get("hist_OFF_bg_color")
        return bg_color
    
    # establece el punto de historia pulsado
    def set_history_index(self, index):
        if self.viewport:
            self.viewport.actionManager.set_action_index(index)
        self.updateActions(self.viewport)





"""
    ................................... clase UPANELINFO
"""
class UPanelInfo(UPanel):

    def __init__(self, parent, setupKey):
        super().__init__(parent, setupKey)

        # Almacena todos los textos introducidos
        self.text_entries = []
        
        # Configurar la ventana
        self.scrolled_text = UText(self, self.parent.font_text, False, self.setup.get("text_height"), self.setup.get("text_bg_color"), self.setup.get("text_fg_color"))
        self.scrolled_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def add_text(self, new_text ):
        self.text_entries.append(new_text)

        self.scrolled_text.setText(new_text+"\n")
        
        self.scrolled_text.yview(tk.END)

    def clear(self):
        self.scrolled_text.setText("", UText.FONT_NORMAL, True)

    def updateLog(self, log_entries):
        self.clear()
        for entry in log_entries:
            self.add_text(entry)