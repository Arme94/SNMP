# Proyecto SNMP

Este proyecto es una aplicación de monitoreo de recursos del sistema (memoria RAM y carga de CPU) utilizando SNMP. La aplicación está construida con Flask y utiliza SQLite para almacenar los datos de monitoreo.

## Requisitos

- Python 3.6 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clona este repositorio:

    ```sh
    git clone https://github.com/tu-usuario/proyecto-snmp.git
    cd proyecto-snmp
    ```
2. Instala las dependencias:

    ```sh
    pip install -r requirements.txt
    ```

3. Borra el archivo monitor.db:

## Ejecución

1. Inicia la aplicación Flask:

    ```sh
    python app.py
    ```

2. Abre tu navegador web y navega a `http://127.0.0.1:5000` para ver la interfaz de monitoreo.

## Estructura del Proyecto

- `app.py`: Archivo principal de la aplicación Flask.
- `monitor_snmp.py`: Contiene las funciones para obtener datos de SNMP y guardarlos en la base de datos.
- `templates/`: Contiene las plantillas HTML para la interfaz de usuario.
- `static/`: Contiene archivos estáticos como CSS y JavaScript.
- `requirements.txt`: Lista de dependencias del proyecto.
- `.gitignore`: Archivos y directorios que deben ser ignorados por Git.

## Funcionalidades

- Monitoreo de memoria RAM y carga de CPU en tiempo real.
- Visualización de datos históricos en gráficos.
- Soporte para monitorear múltiples máquinas.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que te gustaría realizar.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.