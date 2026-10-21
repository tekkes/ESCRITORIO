#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <filesystem>

namespace escritorio::core {

struct BackupResult {
    bool success = false;
    std::wstring zipPath;
    std::string sha256Hex;
    std::wstring errorMessage;
};

/**
 * @brief Gestor de Copias de Seguridad en formato ZIP con suma de verificación SHA-256.
 * 
 * Cumple con:
 * - Empaquetado automático en ./config/backups/ con marca temporal.
 * - Validación de integridad mediante SHA-256.
 * - Rotación configurable de las últimas N copias (por defecto 5).
 */
class BackupManager {
public:
    BackupManager();
    ~BackupManager() = default;

    // Crea una copia de seguridad en ./config/backups/ del proyecto especificado
    BackupResult CreateBackup(const std::filesystem::path& projectPath, int maxBackups = 5);

    // Lista todas las copias disponibles ordenadas de más reciente a más antigua
    std::vector<std::filesystem::path> ListBackups(const std::wstring& projectPrefix = L"") const;

    // Calcula el hash SHA-256 de un archivo en disco
    static std::string ComputeFileSha256(const std::filesystem::path& filePath);

private:
    std::filesystem::path GetBackupsDirectory() const;
    void RotateBackups(const std::wstring& prefix, int maxKeep);
};

} // namespace escritorio::core
