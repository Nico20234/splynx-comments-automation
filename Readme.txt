Splynx Comentarios – Instalador

Este pequeño programa genera todos los días archivos .txt con los comentarios de las órdenes de servicio de Splynx, organizados por:

Fecha

Técnico

Orden de servicio

Los archivos se guardan siempre en:

📂 Carpeta Splynx_Comentarios en tu Escritorio

1. Contenido de la carpeta

La carpeta que te pasaron (por ejemplo SplynxComentariosInstaller) tiene:

splynx_comentarios_hoy.exe
→ Genera comentarios de las órdenes cerradas de HOY.

splynx_comentarios_ayer.exe
→ Genera comentarios de las órdenes cerradas de AYER.

instalar_splynx_comentarios.bat
→ Instala los programas y crea las tareas automáticas.

desinstalar_splynx_comentarios.bat
→ Borra las tareas automáticas y la carpeta instalada.

README.txt
→ Este archivo.

2. Instalación (una sola vez)

Copiá la carpeta completa del instalador en tu PC (por ejemplo en Escritorio o Documentos).

Entrá a la carpeta.

Hacé clic derecho sobre instalar_splynx_comentarios.bat
y elegí “Ejecutar como administrador”.

Se va a abrir una ventana negra (CMD) que:

copia los programas a:
C:\Users\TU_USUARIO\SplynxComentariosTool

crea dos tareas programadas en Windows:

SplynxComentariosHoy → se ejecuta todos los días a las 17:00

SplynxComentariosAyer → se ejecuta todos los días a las 08:00

Cuando aparezca el mensaje de “Instalación completada”, podés cerrar la ventana.

Listo. No tenés que volver a instalar.

3. Qué hace automáticamente

Una vez instalado:

Todos los días a las 17:00:

Se ejecuta splynx_comentarios_hoy.exe

Se generan los comentarios de las órdenes cerradas de HOY.

Todos los días a las 08:00:

Se ejecuta splynx_comentarios_ayer.exe

Se generan los comentarios de las órdenes cerradas de AYER.

Los archivos se guardan en:

Escritorio\
  Splynx_Comentarios\
    AAAA-MM-DD\
      NombreTecnico\
        NombreDeLaOrden.txt


Ejemplo:

C:\Users\juan\Desktop\Splynx_Comentarios\2025-12-08\Andy Medina\Verificación de RED 📡NODO OCAMPO.txt

4. Ejecutar manualmente (opcional)

Si querés forzar la generación de archivos sin esperar al horario:

Abrí la carpeta de instalación:

C:\Users\TU_USUARIO\SplynxComentariosTool


Hacé doble clic en:

splynx_comentarios_hoy.exe → genera HOY

splynx_comentarios_ayer.exe → genera AYER

Los archivos igual se guardan en Escritorio\Splynx_Comentarios\...

5. Desinstalación

Si ya no querés que siga corriendo automáticamente:

Volvé a la carpeta del instalador (SplynxComentariosInstaller).

Hacé clic derecho sobre desinstalar_splynx_comentarios.bat
y elegí “Ejecutar como administrador”.

El script:

elimina las tareas programadas SplynxComentariosHoy y SplynxComentariosAyer.

borra la carpeta C:\Users\TU_USUARIO\SplynxComentariosTool.

👉 La carpeta Splynx_Comentarios del Escritorio no se borra (por si querés conservar los reportes).

6. Requisitos

Conexión a internet.

Acceso a la URL de Splynx de la empresa.

Usuario y token/API configurados en el programa (esto ya lo deja preparado quien armó el instalador).

Windows (10 u 11 recomendado).

7. Problemas frecuentes

1️⃣ No veo archivos nuevos en Splynx_Comentarios:

Revisá si hay comentarios realmente cargados en Splynx para ese día.

Solo se generan archivos para tareas cerradas (closed = 1).

Probá ejecutar manualmente:

splynx_comentarios_hoy.exe o

splynx_comentarios_ayer.exe.

2️⃣ El instalador dice que no puede crear la tarea programada:

Probá ejecutar instalar_splynx_comentarios.bat como administrador.

Verificá que tu usuario tenga permisos para usar el Programador de tareas.

3️⃣ Quiero cambiar los horarios (17:00 / 08:00):

Pedí al que armó el instalador que te genere otra versión del .bat con otros horarios
(o se puede editar el .bat y cambiar /st 17:00 y /st 08:00).