# Flujo de Trabajo Adversarial Multi-Agente (Red Team Verification & Validation Loop)

> **Documento:** `.agents/workflows/redteam_loop.md`  
> **Sistema:** Escritorio - Aplicación Nativa Portable para Windows 11  
> **Rol:** Director de Ciberseguridad Ofensiva y QA Adversarial (Red Team Lead)  
> **Objetivo:** Validación y verificación continua en bucle adversarial cerrado hasta alcanzar CERO errores, carencias o discrepancias respecto a Scrivener 3.

---

## 1. Visión General de la Arquitectura Adversarial

El sistema opera mediante una dinámica de oposición controlada (Red Team vs. Blue Team) compuesta por 4 agentes autónomos especializados. El bucle interactivo se ejecuta de forma automatizada hasta que todos los agentes del Equipo Rojo emitan una evaluación limpia de cero hallazgos.

```mermaid
graph TD
    subgraph Red Team [Equipo Rojo Adversarial]
        A1[Agente 1: ParityInquisitorAgent<br/>Paridad Funcional, Atajos y REA]
        A2[Agente 2: ChaosFuzzerAgent<br/>Estrés 500k, Corrupción y Portabilidad]
        A3[Agente 3: UIUXAdversaryAgent<br/>Temas, Drag & Drop y Compilación]
    end

    subgraph Report [Consolidación y Auditoría]
        R[tests/redteam/reports/audit_iteration_N.json<br/>critical_bugs | missing_features<br/>ui_discrepancies | portability_violations]
    end

    subgraph Blue Team [Equipo Azul de Remediación]
        A4[Agente 4: BlueTeamFixerAgent<br/>Diagnóstico, Parcheo y Recompilación MSVC]
    end

    A1 --> R
    A2 --> R
    A3 --> R
    R -->|total_issues > 0| A4
    A4 -->|Recompilación Exitosa Escritorio.exe| A1
    R -->|total_issues == 0| FIN[🏆 CERO DISCREPANCIAS: APROBADO]
```

---

## 2. Los 4 Agentes Especializados

### Agente 1: `ParityInquisitorAgent` (Auditor de Paridad Funcional y Visual con REA)
- **Misión:** Inspeccionar implacablemente el árbol de código C++/Python y el binario `Escritorio.exe` utilizando las evidencias arquitectónicas de ingeniería inversa (`docs/rea_evidence/REA_Architecture_Evidence.md`) y la Matriz de Requisitos SRS de Scrivener 3.
- **Vectores de Auditoría:**
  * **Atajos de Teclado:** Valida la presencia y conexión en `WM_KEYDOWN` de todos los atajos obligatorios: `Ctrl+1` (Scrivenings), `Ctrl+2` (Corcho), `Ctrl+3` (Esquema), `Ctrl+'` y `Ctrl+"` (División de pantalla), `Ctrl+Shift+L` (Lock in Place), `Ctrl+Shift+I` (Inspector), `Ctrl+Shift+T` (Metas), `Ctrl+Shift+E` (Compilación), `Ctrl+Shift+N` (Plantillas), `Ctrl+8` (Guion), `F11` (Composición libre de distracciones), `F8` (Ciclo de temas) y `F9` (Densidad UI).
  * **Conformidad de Temas:** Comprueba la presencia de las 7 paletas oficiales (`Minimal`, `Carbon`, `SolarizedDark`, `SolarizedLight`, `Sepia`, `Nord`, `Mocha`) y el soporte de importación de archivos `.scrtheme`.
  * **Límites Ergonómicos:** Exige que la barra de herramientas mida $\le 28\,\text{px}$, las cabeceras $\le 24\,\text{px}$ y los iconos $\le 16\,\text{px}$ en el modo Ultra-Compacto.
  * **Firma PE:** Verifica la estructura `MZ` y `PE\0\0` del ejecutable compilado.

### Agente 2: `ChaosFuzzerAgent` (Equipo Rojo de Estrés, Corrupción y Portabilidad en Otro PC)
- **Misión:** Someter al motor a escenarios destructivos y validar la promesa de portabilidad sin instalación ni dependencias externas.
- **Vectores de Auditoría:**
  * **Estrés Masivo:** Genera proyectos con 1.000 documentos y 500.000 palabras en modo Scrivenings para comprobar que no existan cuelgues, desbordamientos de pila ni pérdidas de datos.
  * **Simulación de Corte Eléctrico:** Simula la interrupción abrupta del sistema durante la escritura en disco, verificando que `AtomicStorage` mantenga la versión previa 100% íntegra (Zero Data Loss).
  * **Inyección Caótica Unicode:** Inyecta caracteres CJK (`日本語`, `中文`), texto bidireccional RTL (`العربية`, `עברית`), emojis de plano alto (`🚀🔥✨`) y símbolos matemáticos complejos en `RTFEngine` garantizando round-trip sin pérdidas.
  * **Simulación de Traslado a Otro PC (Windows 11):** Inspecciona el directorio de importaciones PE de `Escritorio.exe` para garantizar que **SOLO** depende de DLLs estándar del sistema operativo Windows 11 (`KERNEL32.dll`, `USER32.dll`, `GDI32.dll`, `DWMAPI.dll`, `COMCTL32.dll`, `UXTHEME.dll`, `MSVCP140.dll`, etc.) y verifica que **NO** escribe un solo byte en el Registro de Windows (`HKEY_CURRENT_USER\Software\...`) ni en `%APPDATA%`.

### Agente 3: `UIUXAdversaryAgent` (Auditor de Interfaz, Temas y Compilación Documental)
- **Misión:** Validar el comportamiento dinámico de la interfaz y la fidelidad de los exportadores editoriales.
- **Vectores de Auditoría:**
  * **Cambio en Caliente de Temas:** Verifica que el conmutador dinámico de temas aplique los cambios instantáneamente sin parpadeo ni fugas de recursos GDI.
  * **Gestor de Pantalla Dividida:** Audita las funciones `SplitVertical`, `SplitHorizontal`, `CloseSplit` y `ToggleLockActivePane`.
  * **Drag & Drop:** Simula el arrastre jerárquico de nodos en el árbol del Binder y en la Pizarra de Corcho sin corrupción de índices.
  * **Instantáneas y Diff:** Verifica la creación de instantáneas y el cálculo de diferencias textuales (LCS delta highlighting).
  * **Compilación Editorial End-to-End:** Compila un manuscrito a `.docx`, `.pdf`, `.epub` y `.fdx`, verificando que las etiquetas `<$n>`, `<$title>` y las notas al pie se resuelvan con precisión quirúrgica.

### Agente 4: `BlueTeamFixerAgent` (Ingeniero de Remediación y Parcheo)
- **Misión:** Recibir el informe estructurado de fallos generado por los 3 agentes del Equipo Rojo, diagnosticar la causa raíz, aplicar parches de código y ejecutar `build.bat` para recompilar `Escritorio.exe`, transfiriendo el control nuevamente al Equipo Rojo.

---

## 3. Protocolo de Ejecución y Métricas

El orquestador produce en cada iteración el archivo:
`tests/redteam/reports/audit_iteration_<N>.json`

Estructura de métricas obligatoria:
```json
{
    "iteration": 1,
    "timestamp": "2026-10-22 18:30:00",
    "counts": {
        "critical_bugs": 0,
        "missing_features": 0,
        "ui_discrepancies": 0,
        "portability_violations": 0,
        "total_issues": 0
    },
    "test_metrics": {
        "passed_tests": 149,
        "failed_tests": 0,
        "success_rate": "100.0%"
    },
    "issues": []
}
```

---

## 4. Instrucciones de Uso

### Ejecutar una iteración de auditoría:
```powershell
python tests/redteam/run_adversarial_suite.py --iterations 1 --no-auto-fix
```

### Ejecutar el bucle continuo adversarial (Red Team vs Blue Team):
```powershell
python tests/redteam/run_adversarial_suite.py --max-iterations 5 --auto-fix
```

O utilizando el launcher directo de Windows:
```cmd
tests\redteam\run_adversarial_suite.bat
```
