@echo on
taskkill /F /im py.exe
taskkill /F /im py.exe
taskkill /F /im py.exe
taskkill /F /im py.exe

powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'python C:\Users\Jotzi1\Desktop\Extraccion_audios_Mariana\main_extracciones.py'"