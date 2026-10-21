#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <filesystem>
#include <map>

namespace escritorio::core {

/**
 * @brief Gestor de portabilidad absoluta ("Copy & Run") para Windows 11.
 * 
 * Garantiza:
 * 1. Detección dinámica de la ruta del ejecutable mediante GetModuleFileNameW.
 * 2. Cero escrituras en el Registro de Windows (HKCU/HKLM) y cero escrituras en %APPDATA%.
 * 3. Rutas relativas para proyectos, plantillas y diccionarios dentro del árbol de la aplicación.
 * 4. Auto-creación de ./config/, ./config/themes/, ./config/templates/, ./config/backups/ y ./config/dictionaries/.
 */
class PortableManager {
public:
    static PortableManager& Instance();

    // Inicializa el entorno portable y valida o genera los directorios locales
    bool Initialize();

    // Rutas absolutas del entorno local de ejecución
    const std::wstring& GetExecutablePath() const { return m_executablePath; }
    const std::wstring& GetAppDirectory() const { return m_appDirectory; }
    const std::wstring& GetConfigDirectory() const { return m_configDirectory; }
    const std::wstring& GetThemesDirectory() const { return m_themesDirectory; }
    const std::wstring& GetTemplatesDirectory() const { return m_templatesDirectory; }
    const std::wstring& GetBackupsDirectory() const { return m_backupsDirectory; }
    const std::wstring& GetDictionariesDirectory() const { return m_dictionariesDirectory; }
    const std::wstring& GetSettingsFilePath() const { return m_settingsFilePath; }

    // Conversión inteligente a rutas relativas para portabilidad de pendrive/disco
    std::wstring ToRelativePath(const std::wstring& absolutePath) const;
    std::wstring ToAbsolutePath(const std::wstring& path) const;

    // Gestión de configuración local (./config/escritorio_settings.json)
    bool LoadSettings();
    bool SaveSettings();
    std::string GetStringSetting(const std::string& key, const std::string& defaultValue = "") const;
    void SetStringSetting(const std::string& key, const std::string& value);

    int GetIntSetting(const std::string& key, int defaultValue = 0) const;
    void SetIntSetting(const std::string& key, int value);

    bool GetBoolSetting(const std::string& key, bool defaultValue = false) const;
    void SetBoolSetting(const std::string& key, bool value);

    // Lista de proyectos recientes (almacenados como rutas relativas si están dentro de la carpeta portable)
    void AddRecentProject(const std::wstring& projectPath);
    std::vector<std::wstring> GetRecentProjects() const;

private:
    PortableManager();
    ~PortableManager() = default;
    PortableManager(const PortableManager&) = delete;
    PortableManager& operator=(const PortableManager&) = delete;

    void EnsureDirectories();
    void CopyDefaultAssetsIfMissing();

    std::wstring m_executablePath;
    std::wstring m_appDirectory;
    std::wstring m_configDirectory;
    std::wstring m_themesDirectory;
    std::wstring m_templatesDirectory;
    std::wstring m_backupsDirectory;
    std::wstring m_dictionariesDirectory;
    std::wstring m_settingsFilePath;

    std::map<std::string, std::string> m_settings;
    std::vector<std::wstring> m_recentProjects;
    bool m_initialized = false;
};

} // namespace escritorio::core
