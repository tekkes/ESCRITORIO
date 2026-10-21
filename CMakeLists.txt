cmake_minimum_required(VERSION 3.20)

project(Escritorio
    VERSION 1.0.0
    DESCRIPTION "Estación de Trabajo Editorial Nativa Portable para Windows 11"
    LANGUAGES CXX RC
)

# Estándar C++20 moderno
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enlace estático estricto del Runtime de C/C++ (/MT en Release, /MTd en Debug)
# Garantiza portabilidad "Copy & Run" sin depender de vcruntime140.dll externo
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

# Rutas de salida para los ejecutables
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/build/release")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/build/release")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/build/debug")

# Fuentes del proyecto nativo
set(SOURCES
    src/main.cpp
    src/core/PortableManager.hpp
    src/core/PortableManager.cpp
    src/core/ProjectEngine.hpp
    src/core/ProjectEngine.cpp
    src/core/BackupManager.hpp
    src/core/BackupManager.cpp
    src/themes/ThemeEngine.hpp
    src/themes/ThemeEngine.cpp
    src/ui/MainWindow.hpp
    src/ui/MainWindow.cpp
    resources.rc
)

# Definición del ejecutable nativo de Windows (Subsistema WINDOWS)
add_executable(Escritorio WIN32 ${SOURCES})

# Configuración de propiedades del objetivo
set_target_properties(Escritorio PROPERTIES
    OUTPUT_NAME "Escritorio"
    WIN32_EXECUTABLE TRUE
)

# Opciones específicas para MSVC / Clang-CL
if(MSVC)
    target_compile_options(Escritorio PRIVATE
        /W4
        /MP
        /permissive-
        /Zc:inline
        /Zc:preprocessor
        $<$<CONFIG:Release>:/O2 /Oi /GL /Gy>
    )

    target_link_options(Escritorio PRIVATE
        /SUBSYSTEM:WINDOWS
        /MANIFEST:NO
        $<$<CONFIG:Release>:/LTCG /OPT:REF /OPT:ICF>
    )
endif()

# Inclusiones
target_include_directories(Escritorio PRIVATE
    ${CMAKE_SOURCE_DIR}/src
)

# Librerías estándar del sistema incluidas de serie en cualquier instalación limpia de Windows 11
target_link_libraries(Escritorio PRIVATE
    kernel32
    user32
    gdi32
    shell32
    shlwapi
    dwmapi
    comctl32
    uxtheme
    ole32
    oleaut32
    advapi32
)

# Copiar archivos de configuración y assets a la carpeta de salida
add_custom_command(TARGET Escritorio POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_SOURCE_DIR}/build/release/config"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_SOURCE_DIR}/build/release/config/themes"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_SOURCE_DIR}/build/release/config/templates"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_SOURCE_DIR}/build/release/config/backups"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_SOURCE_DIR}/build/release/config/dictionaries"
    COMMENT "Inicializando árbol de carpetas portables en build/release/..."
)
