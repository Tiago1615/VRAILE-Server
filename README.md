# 🧠 VRAILE (Virtual Reality Artificial Inteligence Learning Environment)

Este repositorio contiene el servidor local que sirve como intermediario entre la aplicación *VRAILE*. Este servidor está basado en Python y ha sido construido mediante un entorno Conda, que cuenta con un conjunto de dependencias listadas en `requirements.txt`.

- [📦 Requisitos](#-requisitos)
- [📒 Credenciales](#-credenciales)
- [🌍 Red](#-red)
- [⚙️ Instalación](#-instalación)
  - [🐍 Instalar Python y Anaconda](#-instalar-python-y-anaconda)
  - [🔁 Crear el entorno de Conda](#-crear-el-entorno-de-conda)
  - [📚 Instalar las dependencias](#-instalar-las-dependencias)
  - [🖥️ Puesta en marcha del servidor](#️-puesta-en-marcha-del-servidor)

## 📦 Requisitos

- Python 3.11.11
- Conda
- Credenciales de *OpenAI*
- Credenciales de *AWS*
- Red con acceso al exterior

## 📒 Credenciales

En caso de no contar con cuenta en *AWS* u *OpenAI Platform*, será necesario crear una cuenta antes de utilizar este servidor. Puesto que, se emplean los servicios de *AWS Polly* y de los modelos de *IA* generativa de *OpenAI*.

[AWS](https://aws.amazon.com/es/)

[OpenAI Platform](https://platform.openai.com/docs/overview)

Habiendo creado las cuentas, será necesario establecer las *API keys*. Para ello, estos vídeos son recomendables

[API Keys AWS](https://www.youtube.com/watch?v=MQfVCY9qgEU&list=PLrE-FZIEEls1-c7QifZYzeq50Id08FcJo&index=2&t=122s)

[API Keys OpenAI](https://www.youtube.com/watch?v=MQfVCY9qgEU&list=PLrE-FZIEEls1-c7QifZYzeq50Id08FcJo&index=2&t=122s)

Con las respectivas credenciales, se puede actualizar el contenido del archivo `.env` y así hacer uso de los respectivos servicios.

## 🌍 Red

Es necesario contar con acceso a una conexión de red a la que se encuentren conectadas tanto la máquina que va a alojar este servidor como las gafas de *VR* que se van a usar. Para determinar la dirección IP que va a ser usada por el servidor, se dispone del archivo `config.json`.

## ⚙️ Instalación

### 🐍 Instalar Python y Anaconda

Para instalar *Python*, en *Windows* existen dos posibilidades. La primera, desde la propia tienda de *Windows*, buscar *Python* e instalar la versión que convenga. O si no, también existe la opción de descargar e instalarlo desde la web:

[Python](https://www.python.org/downloads/)

En otros sistemas operativos, lo más cómodo probablemente sería usar el enlace anterior, aunque también existe la opción de hacerlo mediante comandos:

[Python en plataformas Unix](https://docs.python.org/es/3.13/using/unix.html)

Para instalar *Anaconda*, independientemente de la plataforma, es tan sencillo como entrar al enlace siguiente, introducir un email y elegir el sistema operativo:

[Anaconda](https://www.anaconda.com/download)

De todas formas, este tutorial está bastante bien:

[Tutorial instalación Anaconda](https://www.youtube.com/watch?v=s49fbb1qlE8&t=362s)

### 🔁 Crear el entorno de Conda

Para crear el entorno de *Anaconda*, se abre el *Anaconda Prompt* y se ejecutan los comandos siguientes:

```bash
conda create -n NOMBRE_ENTORNO python=3.11.11
conda activate NOMBRE_ENTORNO
conda install -n NOMBRE_ENTORNO ipykernel --update-deps --force-reinstall
```

### 📚 Instalar las dependencias

Para instalar las dependencias, desde la consola abierta antes por el *Anaconda Prompt*, es necesario navegar al directorio en el que se encuentra el archivo `requirements.txt` y luego se puede proceder a la instalación, como se muestra aquí:

```bash
cd RUTA_AL_ARCHIVO_requirements.txt
pip install -r requirements.txt
```

### 🖥️ Puesta en marcha del servidor

Primero es necesario abrir el *Anaconda Prompt* y seguidamente, ejecutar los comandos:

```bash
cd RUTA_AL_ARCHIVO_server.py
conda activate NOMBRE_ENTORNO
python server.py
```
