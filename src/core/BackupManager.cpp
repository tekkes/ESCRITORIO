#include "BackupManager.hpp"
#include "PortableManager.hpp"
#include <wincrypt.h>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <algorithm>

#pragma comment(lib, "advapi32.lib")

namespace escritorio::core {

namespace {

std::wstring GetBackupTimestamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm;
    localtime_s(&tm, &t);
    std::wstringstream ss;
    ss << std::put_time(&tm, L"%Y%m%d_%H%M%S");
    return ss.str();
}

} // namespace

BackupManager::BackupManager() {}

std::filesystem::path BackupManager::GetBackupsDirectory() const {
    return PortableManager::Instance().GetBackupsDirectory();
}

std::string BackupManager::ComputeFileSha256(const std::filesystem::path& filePath) {
    HANDLE hFile = CreateFileW(filePath.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_FLAG_SEQUENTIAL_SCAN, nullptr);
    if (hFile == INVALID_HANDLE_VALUE) return "";

    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    std::string result = "";

    if (CryptAcquireContextW(&hProv, nullptr, nullptr, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {
        if (CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)) {
            BYTE buffer[8192];
            DWORD bytesRead = 0;
            BOOL success = TRUE;

            while (ReadFile(hFile, buffer, sizeof(buffer), &bytesRead, nullptr) && bytesRead > 0) {
                if (!CryptHashData(hHash, buffer, bytesRead, 0)) {
                    success = FALSE;
                    break;
                }
            }

            if (success) {
                BYTE hashBytes[32];
                DWORD hashLen = sizeof(hashBytes);
                if (CryptGetHashParam(hHash, HP_HASHVAL, hashBytes, &hashLen, 0)) {
                    std::stringstream ss;
                    for (DWORD i = 0; i < hashLen; ++i) {
                        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hashBytes[i]);
                    }
                    result = ss.str();
                }
            }
            CryptDestroyHash(hHash);
        }
        CryptReleaseContext(hProv, 0);
    }

    CloseHandle(hFile);
    return result;
}

BackupResult BackupManager::CreateBackup(const std::filesystem::path& projectPath, int maxBackups) {
    BackupResult res;
    if (!std::filesystem::exists(projectPath)) {
        res.errorMessage = L"El proyecto no existe en la ruta indicada.";
        return res;
    }

    auto backupDir = GetBackupsDirectory();
    std::filesystem::create_directories(backupDir);

    std::wstring prefix = projectPath.stem().wstring();
    std::wstring zipName = prefix + L"_backup_" + GetBackupTimestamp() + L".zip";
    std::filesystem::path zipTarget = backupDir / zipName;

    // Utilizar tar.exe nativo de Windows (System32\tar.exe) para crear un archivo .zip estándar
    // tar.exe -a -c -f <zipTarget> -C <projectPath> .
    std::wstring cmd = L"tar.exe -a -c -f \"" + zipTarget.wstring() + L"\" -C \"" + projectPath.wstring() + L"\" .";

    STARTUPINFOW si = { sizeof(si) };
    PROCESS_INFORMATION pi = {};
    si.dwFlags |= STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;

    std::vector<wchar_t> cmdBuffer(cmd.begin(), cmd.end());
    cmdBuffer.push_back(0);

    if (CreateProcessW(nullptr, cmdBuffer.data(), nullptr, nullptr, FALSE, CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi)) {
        WaitForSingleObject(pi.hProcess, 30000); // 30s timeout
        DWORD exitCode = 1;
        GetExitCodeProcess(pi.hProcess, &exitCode);
        CloseHandle(pi.hProcess);
        CloseHandle(pi.hThread);

        if (exitCode == 0 && std::filesystem::exists(zipTarget)) {
            // Verificar integridad con SHA-256
            std::string sha = ComputeFileSha256(zipTarget);
            if (!sha.empty()) {
                res.success = true;
                res.zipPath = zipTarget.wstring();
                res.sha256Hex = sha;

                // Aplicar política de rotación
                RotateBackups(prefix, maxBackups);
                return res;
            }
        }
    }

    res.errorMessage = L"Error al empaquetar o verificar la copia de seguridad ZIP.";
    return res;
}

std::vector<std::filesystem::path> BackupManager::ListBackups(const std::wstring& projectPrefix) const {
    std::vector<std::filesystem::path> list;
    auto dir = GetBackupsDirectory();
    if (!std::filesystem::exists(dir)) return list;

    for (const auto& entry : std::filesystem::directory_iterator(dir)) {
        if (entry.path().extension() == L".zip") {
            if (projectPrefix.empty() || entry.path().filename().wstring().rfind(projectPrefix, 0) == 0) {
                list.push_back(entry.path());
            }
        }
    }

    // Ordenar de más reciente a más antiguo por fecha de modificación
    std::sort(list.begin(), list.end(), [](const std::filesystem::path& a, const std::filesystem::path& b) {
        return std::filesystem::last_write_time(a) > std::filesystem::last_write_time(b);
    });

    return list;
}

void BackupManager::RotateBackups(const std::wstring& prefix, int maxKeep) {
    if (maxKeep <= 0) return;
    auto backups = ListBackups(prefix);
    if (static_cast<int>(backups.size()) > maxKeep) {
        for (size_t i = maxKeep; i < backups.size(); ++i) {
            std::error_code ec;
            std::filesystem::remove(backups[i], ec);
        }
    }
}

} // namespace escritorio::core
