# opencvppl
GUI for openCV library in python



La presente aplicación trata de agilizar la aplicación de diversos filtros sobre una imagen mediante OpenCV, permitiendo modificaciones en los parámetros de sus etapas para lograr obtener de forma ágil el resultado deseado.

## Diagrama de Clases

![Diagrama de clases de OpenCVPipeline](https://github.com/gmars76/opencvppl/blob/main/drawio/UML_diagrama_clases_2_0.png?raw=true)

El proyecto se apoya principalmente en la clase **OpenCVPPL**, que es la responsable de realizar toda la interacción con el usuario y de orquestar el funcionamiento de los diferentes módulos y clases que componen el proyecto.
El otro gran pilar del proyecto es la clase **CVUtils**, que en realidad es un compendio de utilidades diversas para la gestión de la librería *OpenCV*:
* Definición de constantes de uso, como Kernels para uso interno o códigos de teclado
* Utilidades varias de uso, a modo de “atajos”: *log(), decimalToPercent(), hexColorToRGBA(), color256ToRGBA(), readImage(), writeImage(), colorToGray() etc*.
* Envoltorio para las funciones de filtro de OpenCV, estandarizando el modo en el que se accede a la funcionalidad de la librería y sirviendo de “puente” para su utilización. Este es el uso principal que se le da en este proyecto. 

## OpenCVPPL

La responsabilidad de esta clase es la interacción de la aplicación con el usuario, preparando la información para que el resto de módulos puedan desarrollar sus funciones. Tiene las siguientes responsabilidades y asociaciones:
* Hereda de la clase tk.Tk, lo que le convierte en la principal fuente de interacción con el usuario, permitiéndole manejar la ventana y los paneles asociados a la misma.
* Utilizando la clase de apoyo USetup, accede al fichero de configuración en formato JSON “opencvPPL.setup.json” dónde se establecen los parámetros de visualización de toda la aplicación (título de la ventana, tipo de letra y tamaño, tamaño y posición de cada uno de los diversos paneles, etc.), y los pone a disposición de sus clases asociadas.
* Asociaciones fundamentales de la aplicación:
	* UViewportManager: gestiona las distintas pestañas de imágenes (UViewport) de la aplicación, y las acciones a realizar en cada una.
	* Upanel{}: diccionario de paneles flotantes de la aplicación (herramientas, información, acciones).
* Gestiona los cuadros de diálogo necesarios con el usuario (seleccionar fichero, aceptar opciones, etc.).
* Gestiona la interacción entre las pestañas (por ejemplo, el cambio de pestaña activa).
* Gestiona la interacción por teclado con el usuario. Lo realiza dinámicamente, de modo que según el filtro que esté activo es capaz de obtener las teclas que reaccionarán al mismo según los parámetros establecidos en el JSON que define la acción (delega la obtención de teclas de una acción en la clase UActionManager). Cuando el usuario pulsa una tecla asociada (dinámicamente como hemos mecionado) al parámetro de una acción, se actualizan los parámetros de la acción y se llama al método action_redo() del viewport actual, que re-ejecutará la operación.
* Funciona como punto de entrada de las acciones ejecutadas en la aplicación, mediante el método add_action(actionName, params). En realidad el método add_action() no ejecuta la acción sino que la prepara si procede para que la clase UViewport la realice realmente en el método do_action(). 

## Módulo UViewport

Formado por las clases UViewportManager y UViewport, y es el encargado de mostrar las pestañas de imagen de la aplicación y gestionarlas.
Las funciones principales que desarrolla la clase **UViewportManager** son las siguientes:
* Hereda de ttk.Notebook, que es un gestor de pestañas de tkinter, y utiliza un vector “tabs” para gestionar las que el usuario va creando. Esto es, gestiona todos los viewports abiertos por el usuario, indicando cuál está activo con el método getCurrentViewport().
* Añade (con el nombre de fichero proporcionado por OpenCVPPL) y cierra pestañas, y gestiona los cambios de pestañas, enviándoselos a OpenCVPPL para que modifique los paneles según la pestaña activa.

La clase **UViewport** es el corazón del módulo y en realidad de la aplicación, es el que realmente opera sobre las imágenes. Sus funciones principales son las siguientes:
* Hereda de ttk.Frame, como contenedor de otros widgets de tkinter (contiene el canvas que mostrará la imagen).
* Contiene referencias al objeto OpenCVPPL principal y al UActionManager, que almacena el historial de acciones sobre la imagen.
* Contiene los textos que aparecen en el panel Info (log_entries)
* Guarda la imagen a visualizar, su nombre de fichero, el zoom de la misma, y si ha sido modificada o no, para mostrar al usuario la confirmación al salir de la pestaña.
* Permite guardar el pipeline (pila de acciones) actual en un json, que incluirá los valores de parámetros introducidos por el usuario.
* Permite abrir un pipeline almacenado previamente en formato json, de forma que la lista de acciones allí almacenadas se apliquen inmediatamente a la imagen actual.
* El método más complejo de la clase es el relacionado con la ejecución de una acción sobre la imagen, que involucra a otros tres métodos:
	* *do_action(self, actionName, params = None, updateHistory = True)*: Llama al método que corresponda según el tipo de acción lanzada. En caso de no ser una acción básica, llama al método *action_execute(actionName, params)* que tratará de ejecutar el método. Antes de finalizar almacena la acción en el histórico de acciones si procede (si es una modificación de un parámetro de un filtro será una re-ejecución y no es necesario almacenarlo de nuevo, simplemente variar sus parámetros). 
	* *action_execute(actionName, params)*: Ejecuta un método dinámicamente según el nombre de la acción y su configuración en *opencvPPL.actions.json*. En el JSON de las acciones se indican el nombre del método de **CVUtils** a ejecutar (el puente entre la aplicación y OpenCV) y los parámetros que necesita, éste método busca el nombre de la acción indicado en el json, averigua sus parámetros (estableciendo automáticamente el parámetro img al del propio viewport) y establece sus valores, ejecutando el método correspondiente.
	* *action_redo()*: Re-ejecuta la última acción, con los parámetros ya modificados desde OpenCVPPL, volviendo un paso atrás en la pila de acciones, y volviendo a ejecutar la acción con los nuevos valores.

## Módulo UActionManager

Formado por las clases UActionManager y UAction, y es el encargado de llevar registro de las acciones aplicadas sobre el UViewport actual.
La clase **UActionManager** administra la pila de acciones de un *UViewport*, y sus funciones fundamentales son:
* Lleva la gestión de las acciones de un UViewport, que almacena en un vector UAction[], al que el viewport va apilando acciones mediante el método *add_history_action(self, actionName, actionParams=None, updateHistory=True)*. 
* Devuelve la configuración de una UAction según su JSON (parámetros, teclas asociadas, valores iniciales, incrementos)
* Gestiona la navegación por el histórico de acciones, re-ejecutando las mismas si algún estado anterior ha sido modificado. Esto se lleva a cabo principalmente con el método *set_action_index(newIndex)*, que es algo más complejo de lo que aparenta: La navegación por la pila de acciones permite que el usuario retroceda, por ejemplo, al paso 3 de 5, modifique el valor de la acción 3 y vuelva a aplicar los pasos 4 y 5. Por tanto, el *UActionManager* debe ser capaz de recordar si algún parámetro ha sido modificado en la pila de acciones (se muestra un asterísco en su título), y si es así, alguna acción anterior ha sido modicada, debe re-ejecutar todos los filtros involucrados actualizando los resultados intermedios de toda la pipeline. Si no hay parámetros modificados, la navegación por la pila no necesita re-ejecución ya que cada UAction lleva un registro de su imagen resultado.
La clase **UAction** es algo más sencilla y tiene las siguientes funciones:
* Es el registro de la acción (filtro) realizado sobre la imagen, con su actionName y sus parámetros asociados.
* Permite recordar si la acción ha sido modificada
* Guarda la imagen resultado de la acción, para permitir la navegación ágil por el pipeline del UViewport.
* Es capaz de incrementar o decrementar el valor de un parámetro según lo que indique su definición en el fichero de configuración de acciones JSON.
* Permite volcarse a JSON para guardar el pipeline actual, obviando los atributos que no apliquen a este fin.
