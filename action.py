from cvUtils import CVUtils, USetup, FileUtils

"""
    ................................... clase UActionManager
"""
class UActionManager():

    JSON_ACTIONS = "opencvPPL.actions.json"
    
    # Configuración
    SETUP = USetup(JSON_ACTIONS)

    ACTION_OPEN = "action_open"
    ACTION_SAVE = "action_save"
    ACTION_PIPELINE_OPEN = "action_pipeline_open"
    ACTION_PIPELINE_SAVE = "action_pipeline_save"
    ACTION_CLOSE = "action_close"
    ACTION_ZOOM_IN = "action_zoom_in"
    ACTION_ZOOM_OUT = "action_zoom_out"

    ACTION_UPSIZE = "action_upSize"
    ACTION_DOWNSIZE = "action_downSize"
    ACTION_BW = "action_colorToGray"
    ACTION_BLURGAUSS = "action_blurGauss"
    ACTION_BLURMEDIAN = "action_blurMedian"
    ACTION_FILTERMIN = "action_filterMin"
    ACTION_FILTERMAX = "action_filterMax"

    ACTION_SOBEL_HOR = "action_sobel_HOR"
    ACTION_SOBEL_VERT = "action_sobel_VERT"

    ACTION_SOBEL_FULL = "action_sobel_FULL"
    ACTION_CANNY = "action_canny"
    ACTION_TRESHOLD = "action_treshold"

    # Devuelve las acciones disponibles con su texto asociado
    @staticmethod
    def get_available_actions():
        available_actions = []
        for action in UActionManager.SETUP.getKeys():
            #print( action+"     "+UActionManager.SETUP.getSetup(action).get("title") )
            available_actions.append( { "key": action, "text": UActionManager.SETUP.getSetup(action).get("title") })
        return available_actions
    
    # Devuelve los datos de la acción
    @staticmethod
    def get_actionSetup(actionName):
        return  UActionManager.SETUP.getSetup(actionName)
    
    # Devuelve array con los parametros variables (las teclas a pulsar)
    @staticmethod
    def get_actionVariableKeys(actionName):
        vars = []
        actionSetup = UActionManager.get_actionSetup(actionName)
        params = actionSetup.get('params')
        for paramName in params.keys():
            if params.get(paramName).get("variable"):
                vars.append( params.get(paramName).get("key") )
        return vars
    
    # Devuelve el nombre del parametro con la key indicada
    @staticmethod
    def get_paramNameByKey(actionName, key):
        paramName = None
        keyValue = key.lower()   # pasa a minúsculakK
        actionSetup = UActionManager.get_actionSetup(actionName)
        params = actionSetup.get('params')
        i = 0
        for paramKey in params.keys():
            if keyValue == params.get(paramKey).get("key"):
                paramName = paramKey
            i += 1
        return paramName
    
    # Devuelve el nombre del parametro con la key indicada
    @staticmethod
    def get_actionTitle(actionName):
        actionSetup = UActionManager.get_actionSetup(actionName)
        return actionSetup.get("title")
    

    def __init__(self, parent):
        self.parent = parent
        self.viewport = parent

        self.actions = []
        self.last_action = None

    def getCurrentAction(self):
        action = None
        if self.last_action is not None and self.last_action >= 0:
            action = self.actions[self.last_action]
        return action

    """
        Añade una nueva acción sobre el objeto:
            - Si había acciones posteriores al last_action, se borran
            - last_action nuevo
    """    
    def add_history_action(self, actionName, actionParams=None, updateHistory=True):
        action_modified = not updateHistory     # si es modified la marca para que el resto de acciones sepan que tienen que rehacerse
        newAction = UAction(self, actionName, self.viewport.img, actionParams, action_modified)

        # Funcionamiento NORMAL: borro todas las acciones posteriores y añado la nueva
        if updateHistory:
            # Recortar la lista hasta el índice dado
            if self.last_action is not None:
                self.actions = self.actions[:self.last_action + 1]
        
            self.actions.append(newAction)
            self.last_action = len(self.actions) - 1

        # Funcionamiento REDO: actualizo simplemente la actual (sobreescribo)
        else:
            self.last_action += 1
            self.actions[self.last_action] = newAction

    # establece el punto de historia pulsado
    def set_action_index(self, newIndex):
        #CVUtils.debug(f">>> ACTION: SUGERIDO newIndex {newIndex}")
        
        if self.last_action is not None and newIndex >= 0 and newIndex < len(self.actions):

            # Si newIndex > self.last_action --> tengo que rehacer las acciones SI existe una modificación
            if newIndex > self.last_action:
                modified_actionIndex = self.get_modified_action(newIndex)
                if modified_actionIndex >= 0:
                    updateHistory = False
                    for actionIndex in range(modified_actionIndex, newIndex+1):
                        action_redo = self.actions[actionIndex]
                        
                        self.last_action = actionIndex-1
                        self.update_viewport()
                        self.viewport.do_action(action_redo.actionName, action_redo.actionParams, updateHistory)
                        self.viewport.openCVPpl.panels_update()
                        self.actions[actionIndex].modified = False
                    if newIndex < len(self.actions)-1:
                        self.actions[newIndex].modified = True

            self.last_action = newIndex
            self.update_viewport()
            #CVUtils.debug(f">>> ACTION: Viewport UPDATE")
    
    def set_action_next(self):
        self.set_action_index(self.last_action+1)

    def set_action_previous(self):
        self.set_action_index(self.last_action-1)

    # Refresca la imagen del viewport (después de realizar un cambio de last_action)
    def update_viewport(self):
        #TODO: hay que re-ejecutar todas las acciones
        self.viewport.img = self.getCurrentAction().img
        self.viewport.display_image()

    # Abre el pipeline del filepath
    def open_pipeline(self, file_path):
        actionsJson = FileUtils.jsonReadFile(file_path)
        return actionsJson
        

    # Salva el pipeline en el filepath (evita las acciones OPEN y SAVE)
    def save_pipeline(self, file_path):
        actionsJson = []

        for actionIndex in range(self.last_action+1):
            action = self.actions[actionIndex]
            if action.actionName not in [UActionManager.ACTION_OPEN, UActionManager.ACTION_SAVE]:
                actionsJson.append(action.actionToJson())
                
        FileUtils.jsonSaveFile(file_path, actionsJson)


    # Devuelve el indice de la primera action con modified=True o -1 en caso contrario
    def get_modified_action(self, index):
        modifiedIndex = -1
        for actionIndex in range(0,index):
            if self.actions[actionIndex].modified == True:
                modifiedIndex = actionIndex
                break
        return modifiedIndex




"""
    ................................... clase UActionManager
"""
class UAction():

    def __init__(self, parent, actionName, img, actionParams=None, modified=False):
        self.parent = parent
        self.actionName = actionName
        self.actionParams = actionParams
        self.modified = modified    # Indica si la acción ha sido una modificación (el resto de la pila superior se debe actualizar)
        self.img = img.copy() 
        

    # Si alguno de sus parametros es variable (tiene tecla modificadora)
    #        Mejor con el static de ActionManager get_actionVariableKeys
    def is_variable(self):
        variable = False
        actionSetup = UActionManager.get_actionSetup(self.actionName)
        params = actionSetup.get('params')
        for paramKey in params.keys():
            variable = variable or params.get(paramKey).get("variable")
        return variable
    
    # Actualiza el parametro del action
    def updateParamValue(self, paramKeyPressed):
        
        paramName = UActionManager.get_paramNameByKey(self.actionName, paramKeyPressed)
        if paramKeyPressed.islower():
            self.paramIncrement(paramName)
        else:
            self.paramDecrement(paramName)
    
    
    def paramIncrement(self, paramName):
        action_setup = UActionManager.SETUP.getSetup(self.actionName)
        increment = action_setup.get("params").get(paramName).get("increment")
        self.actionParams[paramName] += increment
    
    def paramDecrement(self, paramName):
        action_setup = UActionManager.SETUP.getSetup(self.actionName)
        increment = action_setup.get("params").get(paramName).get("increment")
        self.actionParams[paramName] -= increment

    # Pasa el action a JSON (evitando el parametro "img")
    def actionToJson(self):

        paramsJson = {}
        for paramName in self.actionParams.keys():
            if paramName not in [ "img" ]:
                paramsJson[paramName] = self.actionParams[paramName]
        return {
            "actionName": self.actionName
            , "actionParams": paramsJson
        }
        
