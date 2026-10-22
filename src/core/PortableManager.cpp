#include "PortableManager.hpp"
#include <shlwapi.h>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

#pragma comment(lib, "shlwapi.lib")

namespace escritorio::core {

namespace {

// Utilidad para convertir wstring a UTF-8 string
std::string WideToUtf8(const std::wstring& wstr) {
    if (wstr.empty()) return std::string();
    int size = WideCharToMultiByte(CP_UTF8, 0, wstr.data(), static_cast<int>(wstr.size()), nullptr, 0, nullptr, nullptr);
    std::string result(size, 0);
    WideCharToMultiByte(CP_UTF8, 0, wstr.data(), static_cast<int>(wstr.size()), result.data(), size, nullptr, nullptr);
    return result;
}

// Utilidad para convertir UTF-8 string a wstring
std::wstring Utf8ToWide(const std::string& str) {
    if (str.empty()) return std::wstring();
    int size = MultiByteToWideChar(CP_UTF8, 0, str.data(), static_cast<int>(str.size()), nullptr, 0);
    std::wstring result(size, 0);
    MultiByteToWideChar(CP_UTF8, 0, str.data(), static_cast<int>(str.size()), result.data(), size);
    return result;
}

// Normalizar separadores a barra invertida Windows
std::wstring NormalizeSeparators(std::wstring path) {
    std::replace(path.begin(), path.end(), L'/', L'\\');
    return path;
}

} // namespace

PortableManager& PortableManager::Instance() {
    static PortableManager instance;
    return instance;
}

PortableManager::PortableManager() {
    // 1. Detectar la ruta exacta del ejecutable usando GetModuleFileNameW
    std::vector<wchar_t> buffer(MAX_PATH);
    DWORD length = GetModuleFileNameW(nullptr, buffer.data(), static_cast<DWORD>(buffer.size()));

    while (length >= buffer.size()) {
        buffer.resize(buffer.size() * 2);
        length = GetModuleFileNameW(nullptr, buffer.data(), static_cast<DWORD>(buffer.size()));
    }

    m_executablePath = std::wstring(buffer.data(), length);

    // Obtener directorio padre
    std::filesystem::path exeFsPath(m_executablePath);
    m_appDirectory = exeFsPath.parent_path().wstring();

    // 2. Establecer subcarpetas de ./config/
    std::filesystem::path appDir(m_appDirectory);
    m_configDirectory = (appDir / L"config").wstring();
    m_themesDirectory = (appDir / L"config" / L"themes").wstring();
    m_templatesDirectory = (appDir / L"config" / L"templates").wstring();
    m_backupsDirectory = (appDir / L"config" / L"backups").wstring();
    m_dictionariesDirectory = (appDir / L"config" / L"dictionaries").wstring();
    m_settingsFilePath = (appDir / L"config" / L"escritorio_settings.json").wstring();
}

bool PortableManager::Initialize() {
    if (m_initialized) {
        return true;
    }

    // 1. Asegurar la creación de todas las carpetas portables
    EnsureDirectories();

    // 2. Copiar plantillas y temas predeterminados desde ./assets/ si existen
    CopyDefaultAssetsIfMissing();

    // 3. Cargar o generar ./config/escritorio_settings.json
    if (!std::filesystem::exists(m_settingsFilePath)) {
        // Inicializar configuración por defecto
        m_settings["app_name"] = "Escritorio";
        m_settings["version"] = "1.0.0";
        m_settings["portable_mode"] = "true";
        m_settings["theme"] = "dark_obsidian";
        m_settings["font_family"] = "Segoe UI Variable Display";
        m_settings["editor_font"] = "Georgia";
        m_settings["editor_font_size"] = "13";
        m_settings["autosave_interval_ms"] = "2000";
        m_settings["max_backup_copies"] = "5";
        m_settings["system_registry_access"] = "false";
        m_settings["appdata_access"] = "false";

        SaveSettings();
    } else {
        LoadSettings();
    }

    m_initialized = true;
    return true;
}

void PortableManager::EnsureDirectories() {
    std::error_code ec;
    std::filesystem::create_directories(m_configDirectory, ec);
    std::filesystem::create_directories(m_themesDirectory, ec);
    std::filesystem::create_directories(m_templatesDirectory, ec);
    std::filesystem::create_directories(m_backupsDirectory, ec);
    std::filesystem::create_directories(m_dictionariesDirectory, ec);
}

void PortableManager::CopyDefaultAssetsIfMissing() {
    std::filesystem::path appPath(m_appDirectory);
    std::error_code ec;

    // Si existen assets en ../assets o ./assets, poblamos config/themes y config/templates
    std::vector<std::filesystem::path> assetRoots = {
        appPath / L"assets",
        appPath.parent_path() / L"assets",
        appPath.parent_path().parent_path() / L"assets"
    };

    for (const auto& root : assetRoots) {
        if (std::filesystem::exists(root / L"themes", ec)) {
            for (const auto& entry : std::filesystem::directory_iterator(root / L"themes", ec)) {
                auto dest = std::filesystem::path(m_themesDirectory) / entry.path().filename();
                if (!std::filesystem::exists(dest, ec)) {
                    std::filesystem::copy_file(entry.path(), dest, std::filesystem::copy_options::skip_existing, ec);
                }
            }
        }
        if (std::filesystem::exists(root / L"templates", ec)) {
            for (const auto& entry : std::filesystem::directory_iterator(root / L"templates", ec)) {
                auto dest = std::filesystem::path(m_templatesDirectory) / entry.path().filename();
                if (!std::filesystem::exists(dest, ec)) {
                    std::filesystem::copy_file(entry.path(), dest, std::filesystem::copy_options::skip_existing, ec);
                }
            }
        }
    }
}

std::wstring PortableManager::ToRelativePath(const std::wstring& absolutePath) const {
    if (absolutePath.empty()) return L"";

    std::wstring normAbs = NormalizeSeparators(absolutePath);
    std::wstring normApp = NormalizeSeparators(m_appDirectory);

    // Comparación sin distinción de mayúsculas en Windows
    if (normAbs.size() >= normApp.size()) {
        std::wstring prefix = normAbs.substr(0, normApp.size());
        if (_wcsicmp(prefix.c_str(), normApp.c_str()) == 0) {
            std::wstring rel = normAbs.substr(normApp.size());
            if (!rel.empty() && rel[0] == L'\\') {
                rel = rel.substr(1);
            }
            return L".\\" + rel;
        }
    }
    return absolutePath;
}

std::wstring PortableManager::ToAbsolutePath(const std::wstring& path) const {
    if (path.empty()) return L"";

    std::wstring norm = NormalizeSeparators(path);
    if (norm.rfind(L".\\", 0) == 0) {
        // Es relativa: concatenar con app directory
        std::filesystem::path app(m_appDirectory);
        std::filesystem::path rel(norm.substr(2));
        return (app / rel).wstring();
    }

    // Verificar si es absoluta con letra de unidad o UNC
    if (norm.size() >= 3 && norm[1] == L':' && norm[2] == L'\\') {
        return norm;
    }
    if (norm.rfind(L"\\\\", 0) == 0) {
        return norm;
    }

    std::filesystem::path app(m_appDirectory);
    return (app / norm).wstring();
}

bool PortableManager::LoadSettings() {
    std::ifstream file(m_settingsFilePath);
    if (!file.is_open()) return false;

    std::string line;
    while (std::getline(file, line)) {
        // Limpieza básica y parseo de pares "clave": "valor"
        auto colon = line.find(':');
        if (colon != std::string::npos) {
            auto firstQuote = line.find('"');
            auto secondQuote = line.find('"', firstQuote + 1);
            if (firstQuote != std::string::npos && secondQuote != std::string::npos && secondQuote < colon) {
                std::string key = line.substr(firstQuote + 1, secondQuote - firstQuote - 1);
                
                // Buscar valor
                auto valStart = line.find('"', colon);
                if (valStart != std::string::npos) {
                    auto valEnd = line.find('"', valStart + 1);
                    if (valEnd != std::string::npos) {
                        std::string val = line.substr(valStart + 1, valEnd - valStart - 1);
                        m_settings[key] = val;
                    }
                } else {
                    // Valor numérico o booleano
                    std::string rest = line.substr(colon + 1);
                    rest.erase(std::remove_if(rest.begin(), rest.end(), [](char c) {
                        return c == ' ' || c == '\t' || c == ',' || c == '\r' || c == '\n';
                    }), rest.end());
                    if (!rest.empty()) {
                        m_settings[key] = rest;
                    }
                }
            }
        }
    }
    return true;
}

bool PortableManager::SaveSettings() {
    std::ofstream file(m_settingsFilePath);
    if (!file.is_open()) return false;

    file << "{\n";
    file << "  \"app_name\": \"" << m_settings["app_name"] << "\",\n";
    file << "  \"version\": \"" << m_settings["version"] << "\",\n";
    file << "  \"portable_mode\": true,\n";
    file << "  \"system_registry_access\": false,\n";
    file << "  \"appdata_access\": false,\n";
    file << "  \"theme\": \"" << GetStringSetting("theme", "dark_obsidian") << "\",\n";
    file << "  \"font_family\": \"" << GetStringSetting("font_family", "Segoe UI Variable Display") << "\",\n";
    file << "  \"editor_font\": \"" << GetStringSetting("editor_font", "Georgia") << "\",\n";
    file << "  \"editor_font_size\": " << GetIntSetting("editor_font_size", 13) << ",\n";
    file << "  \"autosave_interval_ms\": " << GetIntSetting("autosave_interval_ms", 2000) << ",\n";
    file << "  \"max_backup_copies\": " << GetIntSetting("max_backup_copies", 5) << ",\n";
    file << "  \"recent_projects\": [\n";

    for (size_t i = 0; i < m_recentProjects.size(); ++i) {
        std::string utf8Path = WideToUtf8(m_recentProjects[i]);
        file << "    \"" << utf8Path << "\"" << (i + 1 < m_recentProjects.size() ? "," : "") << "\n";
    }

    file << "  ]\n";
    file << "}\n";
    return true;
}

std::string PortableManager::GetStringSetting(const std::string& key, const std::string& defaultValue) const {
    auto it = m_settings.find(key);
    return (it != m_settings.end()) ? it->second : defaultValue;
}

void PortableManager::SetStringSetting(const std::string& key, const std::string& value) {
    m_settings[key] = value;
}

int PortableManager::GetIntSetting(const std::string& key, int defaultValue) const {
    auto it = m_settings.find(key);
    if (it != m_settings.end()) {
        try {
            return std::stoi(it->second);
        } catch (...) {}
    }
    return defaultValue;
}

void PortableManager::SetIntSetting(const std::string& key, int value) {
    m_settings[key] = std::to_string(value);
}

bool PortableManager::GetBoolSetting(const std::string& key, bool defaultValue) const {
    auto it = m_settings.find(key);
    if (it != m_settings.end()) {
        return (it->second == "true" || it->second == "1");
    }
    return defaultValue;
}

void PortableManager::SetBoolSetting(const std::string& key, bool value) {
    m_settings[key] = value ? "true" : "false";
}

void PortableManager::AddRecentProject(const std::wstring& projectPath) {
    // Convertir a ruta relativa si está dentro del árbol portable
    std::wstring rel = ToRelativePath(projectPath);

    // Evitar duplicados
    auto it = std::find(m_recentProjects.begin(), m_recentProjects.end(), rel);
    if (it != m_recentProjects.end()) {
        m_recentProjects.erase(it);
    }
    m_recentProjects.insert(m_recentProjects.begin(), rel);

    // Limitar a los 10 más recientes
    if (m_recentProjects.size() > 10) {
        m_recentProjects.resize(10);
    }
    SaveSettings();
}

std::vector<std::wstring> PortableManager::GetRecentProjects() const {
    std::vector<std::wstring> absolutePaths;
    for (const auto& p : m_recentProjects) {
        absolutePaths.push_back(ToAbsolutePath(p));
    }
    return absolutePaths;
}

} // namespace escritorio::core
