# Escritorio

> **Estación de Trabajo Editorial Nativa y 100% Portable para Windows 11**  
> Réplica exacta de funcionalidades, arquitectura, almacenamiento y temas visuales de Scrivener 3 para Windows.

---

## 🌟 Características Principales

- **100% Portable & Zero-Installer:** Un único binario rápido y ligero capaz de ejecutarse desde cualquier memoria USB o carpeta sin escribir en el Registro de Windows ni en carpetas del sistema.
- **Persistencia Atómica Transaccional:** Inmunidad contra cortes de energía mediante escritura en staging (`.tmp`), validación SHA-256 y sustitución atómica vía API nativa `ReplaceFileW`.
- **Compatibilidad Bidireccional:** Soporte nativo para proyectos Scrivener 3 (`.scriv` / `.scrivx`) y formato nativo ultrarrápido (`.escr` / `.escrx`).
- **Vistas Integradas:**
  - **Binder:** Árbol jerárquico con carpetas del sistema (Manuscrito, Investigación, Papelera).
  - **Editor RTF:** Formato de texto enriquecido, recuento métrico en tiempo real y anotaciones.
  - **Split View:** Vistas divididas horizontales y verticales.
  - **Corkboard (Corcho):** Tarjetas virtuales con sinopsis, alfileres de colores y reordenación visual.
  - **Outliner (Esquematizador):** Vista tabular tipo hoja de cálculo con columnas configurables.
  - **Inspector:** Sinopsis, notas, metadatos, marcadores, comentarios e instantáneas (snapshots).
  - **Composition Mode:** Modo de pantalla completa libre de distracciones con atenuación de fondo.
- **Motor de Temas:** Soporte para paquetes `.scrtheme` y `.escrtheme` con paletas predefinidas (Dark Obsidian, Minimal Nord, Solarized Warm, Sepia Classic, Scrivener Classic Light) y *Live Theme Studio*.
- **Herramientas de Autor:** Metas de proyecto (Project Targets), Enfoque Lingüístico (Linguistic Focus), Estadísticas avanzadas de legibilidad, Generador de Nombres de Personajes y Scratchpad global.

---

## 📁 Estructura del Repositorio

```
M:\61_PROYECTOS_IA\18_ESCRITORIO
├── assets/
│   ├── icons/            # Iconos vectoriales SVG (16x16)
│   ├── templates/        # Plantillas (Novela, Ensayo, Guion, Investigación)
│   └── themes/           # Temas integrados JSON/QSS
├── docs/
│   └── rea_evidence/     # Especificación de ingeniería inversa REA
├── portable_config/      # Configuración y backups portables
│   ├── backups/          # Copias de seguridad ZIP automáticas
│   ├── settings/         # Preferencias de la aplicación
│   └── portable_app.json # Manifiesto de modo portable
├── src/
│   ├── compile/          # Motor de compilación multihilo y exportadores
│   ├── core/             # Almacenamiento atómico, XML/RTF, UUIDs, proyectos
│   ├── themes/           # Motor de temas, parser y Live Theme Studio
│   ├── tools/            # Metas, estadísticas, lingüística, generador
│   └── ui/               # Binder, Editor, Corcho, Esquematizador, Inspector
├── tests/
│   └── redteam/          # Suite de validación y pruebas adversariales
├── .gitignore
├── main.py
└── README.md
```

---

## 🧪 Pruebas de Regresión y Validación Adversarial

Para ejecutar la suite de pruebas:

```bash
python -m unittest discover -s tests/redteam
```

---

## 📜 Licencia y Autoría

Desarrollado para el ecosistema **Escritorio** por **tekkes**.
