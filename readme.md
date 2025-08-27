# Comando para el instalador
🎬 KomarcaLabs Video Optimizer

KomarcaLabs Video Optimizer es una aplicación de escritorio multiplataforma (Windows/macOS) desarrollada en Python con PyQt6 que permite optimizar videos para streaming progresivo, asegurando que se puedan reproducir antes de descargarse por completo.

Características

Selección de carpeta de origen y carpeta de salida (opcional).

Detecta automáticamente los archivos de video (.mp4, .mov, .mkv, .avi) y los lista en la interfaz.

Optimización rápida de videos usando ffmpeg con -movflags +faststart.

Nombres de salida legibles con formato nombre_video_opt.ext.

Evita procesar videos ya optimizados.

Carpeta de salida por defecto _optimized dentro de la carpeta de origen.

Verificación visual de si los videos optimizados están listos para streaming usando ffprobe.

Logs en consola detallados para seguir el progreso de la optimización.



# Instalador generacion 
pyinstaller --onefile --windowed --icon=icon.ico --add-binary "ffmpeg.exe:." --add-binary "ffprobe.exe:." main.py
# KStream
