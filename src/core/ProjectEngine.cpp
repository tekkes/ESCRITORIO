#include "ProjectEngine.hpp"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <functional>
#include <objbase.h>

#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "advapi32.lib")

namespace escritorio::core {

namespace {

// Generador de UUID v4 en formato estándar de Scrivener 3 (ej. 7C9B1F20-A03B-44F1-8B66-1029482810AA)
std::wstring GenerateUuid() {
    GUID guid;
    if (CoCreateGuid(&guid) == S_OK) {
        wchar_t szGuid[64] = { 0 };
        StringFromGUID2(guid, szGuid, 64);
        std::wstring s(szGuid);
        // Quitar corchetes { y }
        if (!s.empty() && s.front() == L'{') s.erase(0, 1);
        if (!s.empty() && s.back() == L'}') s.pop_back();
        return s;
    }
    return L"00000000-0000-0000-0000-000000000000";
}

std::wstring GetCurrentIsoTimestamp() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm;
    localtime_s(&tm, &t);
    std::wstringstream ss;
    ss << std::put_time(&tm, L"%Y-%m-%d %H:%M:%S");
    return ss.str();
}

std::string WideToUtf8(const std::wstring& wstr) {
    if (wstr.empty()) return std::string();
    int size = WideCharToMultiByte(CP_UTF8, 0, wstr.data(), static_cast<int>(wstr.size()), nullptr, 0, nullptr, nullptr);
    std::string result(size, 0);
    WideCharToMultiByte(CP_UTF8, 0, wstr.data(), static_cast<int>(wstr.size()), result.data(), size, nullptr, nullptr);
    return result;
}

std::wstring Utf8ToWide(const std::string& str) {
    if (str.empty()) return std::wstring();
    int size = MultiByteToWideChar(CP_UTF8, 0, str.data(), static_cast<int>(str.size()), nullptr, 0);
    std::wstring result(size, 0);
    MultiByteToWideChar(CP_UTF8, 0, str.data(), static_cast<int>(str.size()), result.data(), size);
    return result;
}

std::wstring EscapeXml(const std::wstring& text) {
    std::wstring out;
    for (wchar_t c : text) {
        switch (c) {
        case L'&': out += L"&amp;"; break;
        case L'<': out += L"&lt;"; break;
        case L'>': out += L"&gt;"; break;
        case L'"': out += L"&quot;"; break;
        case L'\'': out += L"&apos;"; break;
        default: out += c; break;
        }
    }
    return out;
}

} // namespace

std::wstring BinderTypeToString(BinderItemType type) {
    switch (type) {
    case BinderItemType::DraftFolder: return L"DraftFolder";
    case BinderItemType::ResearchFolder: return L"ResearchFolder";
    case BinderItemType::TrashFolder: return L"TrashFolder";
    case BinderItemType::Folder: return L"Folder";
    case BinderItemType::Text: return L"Text";
    case BinderItemType::PDF: return L"PDF";
    case BinderItemType::Image: return L"Image";
    case BinderItemType::Media: return L"Media";
    case BinderItemType::WebArchive: return L"WebArchive";
    }
    return L"Text";
}

BinderItemType StringToBinderType(const std::wstring& str) {
    if (str == L"DraftFolder") return BinderItemType::DraftFolder;
    if (str == L"ResearchFolder") return BinderItemType::ResearchFolder;
    if (str == L"TrashFolder") return BinderItemType::TrashFolder;
    if (str == L"Folder") return BinderItemType::Folder;
    if (str == L"Text") return BinderItemType::Text;
    if (str == L"PDF") return BinderItemType::PDF;
    if (str == L"Image") return BinderItemType::Image;
    if (str == L"Media") return BinderItemType::Media;
    if (str == L"WebArchive") return BinderItemType::WebArchive;
    return BinderItemType::Text;
}

// ==============================================================================
// BinderItem: Implementación de Carga Diferida y Guardado Atómico
// ==============================================================================

BinderItem::BinderItem(const std::wstring& uuid, BinderItemType type, const std::wstring& title, ProjectEngine* engine)
    : m_uuid(uuid), m_type(type), m_title(title), m_engine(engine) {
    m_created = GetCurrentIsoTimestamp();
    m_modifiedDate = m_created;
    m_lastModifiedTime = std::chrono::steady_clock::now();
}

std::filesystem::path BinderItem::GetDataDirectory() const {
    if (!m_engine) return {};
    return m_engine->GetProjectPath() / L"Files" / L"Data" / m_uuid;
}

void BinderItem::AddChild(std::shared_ptr<BinderItem> child) {
    if (!child) return;
    child->SetParent(shared_from_this());
    m_children.push_back(child);
    m_modified = true;
}

bool BinderItem::RemoveChild(const std::wstring& uuid) {
    auto it = std::remove_if(m_children.begin(), m_children.end(), [&](const std::shared_ptr<BinderItem>& item) {
        return item->GetUuid() == uuid;
    });
    if (it != m_children.end()) {
        m_children.erase(it, m_children.end());
        m_modified = true;
        return true;
    }
    return false;
}

std::shared_ptr<BinderItem> BinderItem::FindDescendant(const std::wstring& uuid) {
    if (m_uuid == uuid) return shared_from_this();
    for (const auto& child : m_children) {
        auto found = child->FindDescendant(uuid);
        if (found) return found;
    }
    return nullptr;
}

std::string BinderItem::GetContentRtf() {
    if (m_contentRtf.has_value()) {
        return m_contentRtf.value();
    }
    // Carga diferida desde disco
    auto p = GetDataDirectory() / L"content.rtf";
    if (std::filesystem::exists(p)) {
        std::ifstream f(p, std::ios::binary);
        if (f.is_open()) {
            std::stringstream buffer;
            buffer << f.rdbuf();
            m_contentRtf = buffer.str();
            return m_contentRtf.value();
        }
    }
    // Contenido RTF inicial vacío por defecto
    m_contentRtf = "{\\rtf1\\ansi\\ansicpg1252\\deff0\\nouicompat{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}}\\viewkind4\\uc1\\pard\\f0\\fs24\\par}";
    return m_contentRtf.value();
}

void BinderItem::SetContentRtf(const std::string& rtf) {
    m_contentRtf = rtf;
    m_isDirty = true;
    m_modified = true;
    m_modifiedDate = GetCurrentIsoTimestamp();
    m_lastModifiedTime = std::chrono::steady_clock::now();
}

std::string BinderItem::GetSynopsis() {
    if (m_synopsis.has_value()) {
        return m_synopsis.value();
    }
    auto p = GetDataDirectory() / L"synopsis.txt";
    if (std::filesystem::exists(p)) {
        std::ifstream f(p, std::ios::binary);
        if (f.is_open()) {
            std::stringstream buffer;
            buffer << f.rdbuf();
            m_synopsis = buffer.str();
            return m_synopsis.value();
        }
    }
    m_synopsis = "";
    return m_synopsis.value();
}

void BinderItem::SetSynopsis(const std::string& synopsis) {
    m_synopsis = synopsis;
    m_isDirty = true;
    m_modified = true;
    m_modifiedDate = GetCurrentIsoTimestamp();
    m_lastModifiedTime = std::chrono::steady_clock::now();
}

std::string BinderItem::GetNotesRtf() {
    if (m_notesRtf.has_value()) {
        return m_notesRtf.value();
    }
    auto p = GetDataDirectory() / L"notes.rtf";
    if (std::filesystem::exists(p)) {
        std::ifstream f(p, std::ios::binary);
        if (f.is_open()) {
            std::stringstream buffer;
            buffer << f.rdbuf();
            m_notesRtf = buffer.str();
            return m_notesRtf.value();
        }
    }
    m_notesRtf = "";
    return m_notesRtf.value();
}

void BinderItem::SetNotesRtf(const std::string& notes) {
    m_notesRtf = notes;
    m_isDirty = true;
    m_modified = true;
    m_modifiedDate = GetCurrentIsoTimestamp();
    m_lastModifiedTime = std::chrono::steady_clock::now();
}

std::string BinderItem::GetCommentsXml() {
    if (m_commentsXml.has_value()) {
        return m_commentsXml.value();
    }
    auto p = GetDataDirectory() / L"content.comments";
    if (std::filesystem::exists(p)) {
        std::ifstream f(p, std::ios::binary);
        if (f.is_open()) {
            std::stringstream buffer;
            buffer << f.rdbuf();
            m_commentsXml = buffer.str();
            return m_commentsXml.value();
        }
    }
    m_commentsXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Comments Version=\"1.0\"/>";
    return m_commentsXml.value();
}

void BinderItem::SetCommentsXml(const std::string& comments) {
    m_commentsXml = comments;
    m_isDirty = true;
    m_modified = true;
    m_modifiedDate = GetCurrentIsoTimestamp();
    m_lastModifiedTime = std::chrono::steady_clock::now();
}

bool BinderItem::WriteAtomicFile(const std::filesystem::path& targetFile, const std::string& data) {
    std::filesystem::create_directories(targetFile.parent_path());
    std::wstring tmpPath = targetFile.wstring() + L".tmp";

    // 1. Escritura inicial en archivo temporal
    HANDLE hFile = CreateFileW(
        tmpPath.c_str(),
        GENERIC_WRITE,
        0,
        nullptr,
        CREATE_ALWAYS,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );

    if (hFile == INVALID_HANDLE_VALUE) {
        return false;
    }

    DWORD written = 0;
    BOOL ok = WriteFile(hFile, data.data(), static_cast<DWORD>(data.size()), &written, nullptr);
    if (ok) {
        // Forzar vaciado de buffers físicos a disco
        FlushFileBuffers(hFile);
    }
    CloseHandle(hFile);

    if (!ok) {
        DeleteFileW(tmpPath.c_str());
        return false;
    }

    // 2. Reemplazo atómico con MoveFileExW
    BOOL moved = MoveFileExW(
        tmpPath.c_str(),
        targetFile.wstring().c_str(),
        MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH
    );

    if (!moved) {
        // Fallback a ReplaceFileW
        moved = ReplaceFileW(
            targetFile.wstring().c_str(),
            tmpPath.c_str(),
            nullptr,
            REPLACEFILE_WRITE_THROUGH | REPLACEFILE_IGNORE_MERGE_ERRORS,
            nullptr,
            nullptr
        );
        if (!moved) {
            DeleteFileW(tmpPath.c_str());
            return false;
        }
    }

    return true;
}

bool BinderItem::SaveIfDirty() {
    if (!m_isDirty) return false;

    auto dataDir = GetDataDirectory();
    if (m_contentRtf.has_value()) {
        WriteAtomicFile(dataDir / L"content.rtf", m_contentRtf.value());
    }
    if (m_synopsis.has_value()) {
        WriteAtomicFile(dataDir / L"synopsis.txt", m_synopsis.value());
    }
    if (m_notesRtf.has_value()) {
        WriteAtomicFile(dataDir / L"notes.rtf", m_notesRtf.value());
    }
    if (m_commentsXml.has_value()) {
        WriteAtomicFile(dataDir / L"content.comments", m_commentsXml.value());
    }

    m_isDirty = false;
    return true;
}

// ==============================================================================
// ProjectEngine: Implementación del Motor de Proyectos
// ==============================================================================

ProjectEngine::ProjectEngine() {}

ProjectEngine::~ProjectEngine() {
    Close();
}

std::filesystem::path ProjectEngine::GetMasterXmlPath() const {
    std::wstring ext = m_isNative ? L".escrx" : L".scrivx";
    std::wstring stem = m_projectPath.stem().wstring();
    return m_projectPath / (stem + ext);
}

bool ProjectEngine::IsLocked(ProjectLockInfo* outInfo) const {
    auto lockPath = m_projectPath / L"project.lock";
    if (!std::filesystem::exists(lockPath)) {
        return false;
    }

    // Leer contenido del cerrojo
    std::ifstream file(lockPath);
    if (!file.is_open()) return true;

    DWORD pid = 0;
    std::string line;
    std::wstring host, user, ts;

    while (std::getline(file, line)) {
        if (line.find("pid:") == 0) {
            pid = static_cast<DWORD>(std::stoul(line.substr(4)));
        } else if (line.find("host:") == 0) {
            host = Utf8ToWide(line.substr(5));
        } else if (line.find("user:") == 0) {
            user = Utf8ToWide(line.substr(5));
        } else if (line.find("time:") == 0) {
            ts = Utf8ToWide(line.substr(5));
        }
    }

    if (outInfo) {
        outInfo->pid = pid;
        outInfo->hostname = host;
        outInfo->username = user;
        outInfo->timestamp = ts;
    }

    // Verificar si el proceso con dicho PID sigue activo en el sistema
    if (pid != 0) {
        HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
        if (hProcess != nullptr) {
            DWORD exitCode = 0;
            if (GetExitCodeProcess(hProcess, &exitCode) && exitCode == STILL_ACTIVE) {
                CloseHandle(hProcess);
                return true; // Bloqueo activo real
            }
            CloseHandle(hProcess);
        }
    }

    // El proceso ya no existe: es un cerrojo obsoleto (stale lock)
    return false;
}

bool ProjectEngine::AcquireLock() {
    auto lockPath = m_projectPath / L"project.lock";
    DWORD currentPid = GetCurrentProcessId();

    wchar_t hostBuffer[MAX_COMPUTERNAME_LENGTH + 1] = { 0 };
    DWORD hostSize = MAX_COMPUTERNAME_LENGTH + 1;
    GetComputerNameW(hostBuffer, &hostSize);

    wchar_t userBuffer[256] = { 0 };
    DWORD userSize = 256;
    GetUserNameW(userBuffer, &userSize);

    std::wstring ts = GetCurrentIsoTimestamp();

    std::ofstream file(lockPath);
    if (!file.is_open()) return false;

    file << "pid:" << currentPid << "\n";
    file << "host:" << WideToUtf8(hostBuffer) << "\n";
    file << "user:" << WideToUtf8(userBuffer) << "\n";
    file << "time:" << WideToUtf8(ts) << "\n";
    file.flush();

    m_hasLock = true;
    return true;
}

void ProjectEngine::ReleaseLock() {
    if (m_hasLock) {
        auto lockPath = m_projectPath / L"project.lock";
        std::error_code ec;
        std::filesystem::remove(lockPath, ec);
        m_hasLock = false;
    }
}

std::shared_ptr<ProjectEngine> ProjectEngine::CreateNew(const std::wstring& directoryPath, const std::wstring& title, bool isNative) {
    std::filesystem::path p(directoryPath);
    std::wstring ext = isNative ? L".escr" : L".scriv";
    if (p.extension().wstring() != ext) {
        p += ext;
    }

    std::filesystem::create_directories(p / L"Files" / L"Data");
    std::filesystem::create_directories(p / L"Files" / L"Snapshots");
    std::filesystem::create_directories(p / L"Settings");

    auto engine = std::make_shared<ProjectEngine>();
    engine->m_projectPath = p;
    engine->m_isNative = isNative;
    engine->m_title = title;
    engine->m_identifier = GenerateUuid();
    engine->m_draftTargetWords = 50000;
    engine->m_sessionTargetWords = 1500;

    // Crear elementos raíz estándar
    auto draft = std::make_shared<BinderItem>(GenerateUuid(), BinderItemType::DraftFolder, L"Manuscrito", engine.get());
    draft->MetaData().includeInCompile = true;
    draft->MetaData().sectionType = L"Structure Based";

    auto research = std::make_shared<BinderItem>(GenerateUuid(), BinderItemType::ResearchFolder, L"Investigación", engine.get());
    research->MetaData().includeInCompile = false;

    auto trash = std::make_shared<BinderItem>(GenerateUuid(), BinderItemType::TrashFolder, L"Papelera", engine.get());
    trash->MetaData().includeInCompile = false;

    engine->m_rootItems.push_back(draft);
    engine->m_rootItems.push_back(research);
    engine->m_rootItems.push_back(trash);

    // Inicializar etiquetas y estados predeterminados
    engine->SetLabel(-1, L"Ninguna", L"1.0 1.0 1.0 0.0");
    engine->SetLabel(1, L"Concepto", L"0.95 0.26 0.21 1.0");
    engine->SetLabel(2, L"Capítulo", L"0.13 0.59 0.95 1.0");
    engine->SetLabel(3, L"Escena", L"0.30 0.69 0.31 1.0");

    engine->SetStatus(-1, L"Ninguno");
    engine->SetStatus(1, L"Por hacer");
    engine->SetStatus(2, L"Primer borrador");
    engine->SetStatus(3, L"Borrador revisado");
    engine->SetStatus(4, L"Completado");

    engine->SetSectionType(L"Structure Based", L"Según estructura");
    engine->SetSectionType(L"Heading", L"Encabezado");
    engine->SetSectionType(L"Chapter", L"Capítulo");
    engine->SetSectionType(L"Scene", L"Escena");

    // Guardar XML inicial y adquirir cerrojo
    engine->AcquireLock();
    engine->Save();

    return engine;
}

std::shared_ptr<ProjectEngine> ProjectEngine::Open(const std::wstring& directoryPath, bool forceUnlock) {
    std::filesystem::path p(directoryPath);
    if (!std::filesystem::exists(p) || !std::filesystem::is_directory(p)) {
        return nullptr;
    }

    auto engine = std::make_shared<ProjectEngine>();
    engine->m_projectPath = p;
    engine->m_isNative = (_wcsicmp(p.extension().c_str(), L".escr") == 0);

    // Comprobar bloqueo concurrente
    ProjectLockInfo lockInfo;
    if (engine->IsLocked(&lockInfo) && !forceUnlock) {
        // El proyecto está activamente bloqueado por otra instancia
        return nullptr;
    }

    engine->AcquireLock();
    if (!engine->ParseMasterXml()) {
        engine->ReleaseLock();
        return nullptr;
    }

    return engine;
}

void ProjectEngine::Close() {
    Save();
    ReleaseLock();
}

std::shared_ptr<BinderItem> ProjectEngine::GetRootItem(size_t index) const {
    if (index < m_rootItems.size()) {
        return m_rootItems[index];
    }
    return nullptr;
}

std::shared_ptr<BinderItem> ProjectEngine::FindItem(const std::wstring& uuid) const {
    for (const auto& root : m_rootItems) {
        auto found = root->FindDescendant(uuid);
        if (found) return found;
    }
    return nullptr;
}

std::shared_ptr<BinderItem> ProjectEngine::AddItem(const std::wstring& parentUuid, const std::wstring& title, BinderItemType type) {
    auto newItem = std::make_shared<BinderItem>(GenerateUuid(), type, title, this);
    auto parent = FindItem(parentUuid);
    if (parent) {
        parent->AddChild(newItem);
    } else {
        m_rootItems.push_back(newItem);
    }
    m_isDirty = true;
    return newItem;
}

void ProjectEngine::SetLabel(int id, const std::wstring& name, const std::wstring& colorRgba) {
    m_labels[id] = { id, name, colorRgba };
    m_isDirty = true;
}

void ProjectEngine::SetStatus(int id, const std::wstring& name) {
    m_statuses[id] = { id, name };
    m_isDirty = true;
}

void ProjectEngine::SetSectionType(const std::wstring& id, const std::wstring& name) {
    m_sectionTypes[id] = name;
    m_isDirty = true;
}

int ProjectEngine::AutosavePendingChanges(int inactivityThresholdMs) {
    auto now = std::chrono::steady_clock::now();
    int count = 0;

    std::function<void(const std::shared_ptr<BinderItem>&)> checkItem = [&](const std::shared_ptr<BinderItem>& item) {
        if (item->IsDirty()) {
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - item->GetLastModifiedTime()).count();
            if (elapsed >= inactivityThresholdMs) {
                if (item->SaveIfDirty()) {
                    count++;
                }
            }
        }
        for (const auto& child : item->GetChildren()) {
            checkItem(child);
        }
    };

    for (const auto& root : m_rootItems) {
        checkItem(root);
    }

    if (count > 0 || m_isDirty) {
        SerializeMasterXml();
        m_isDirty = false;
    }

    return count;
}

bool ProjectEngine::Save() {
    // Guardar todos los elementos sucios inmediatamente
    std::function<void(const std::shared_ptr<BinderItem>&)> flushItem = [&](const std::shared_ptr<BinderItem>& item) {
        item->SaveIfDirty();
        for (const auto& child : item->GetChildren()) {
            flushItem(child);
        }
    };

    for (const auto& root : m_rootItems) {
        flushItem(root);
    }

    bool ok = SerializeMasterXml();
    m_isDirty = false;
    return ok;
}

// ==============================================================================
// Serialización y Parsing XML Manual Ultra-Robusto (Sin librerías externas)
// ==============================================================================

namespace {

void SerializeBinderItemXml(std::wstringstream& ss, const std::shared_ptr<BinderItem>& item, int indent) {
    std::wstring pad(indent * 4, L' ');
    ss << pad << L"<BinderItem UUID=\"" << item->GetUuid() << L"\" Type=\"" << BinderTypeToString(item->GetType()) << L"\"";
    if (!item->GetCreated().empty()) ss << L" Created=\"" << item->GetCreated() << L"\"";
    if (!item->GetModified().empty()) ss << L" Modified=\"" << item->GetModified() << L"\"";
    ss << L">\n";

    ss << pad << L"    <Title>" << EscapeXml(item->GetTitle()) << L"</Title>\n";

    // MetaData
    ss << pad << L"    <MetaData>\n";
    ss << pad << L"        <IncludeInCompile>" << (item->MetaData().includeInCompile ? L"Yes" : L"No") << L"</IncludeInCompile>\n";
    ss << pad << L"        <SectionType>" << EscapeXml(item->MetaData().sectionType) << L"</SectionType>\n";
    if (item->MetaData().labelId != -1) ss << pad << L"        <LabelID>" << item->MetaData().labelId << L"</LabelID>\n";
    if (item->MetaData().statusId != -1) ss << pad << L"        <StatusID>" << item->MetaData().statusId << L"</StatusID>\n";
    if (!item->MetaData().fileExtension.empty()) ss << pad << L"        <FileExtension>" << item->MetaData().fileExtension << L"</FileExtension>\n";

    if (!item->MetaData().customMetaData.empty()) {
        ss << pad << L"        <CustomMetaData>\n";
        for (const auto& [k, v] : item->MetaData().customMetaData) {
            ss << pad << L"            <Field ID=\"" << EscapeXml(k) << L"\">" << EscapeXml(v) << L"</Field>\n";
        }
        ss << pad << L"        </CustomMetaData>\n";
    }

    if (!item->MetaData().keywords.empty()) {
        ss << pad << L"        <Keywords>\n";
        for (const auto& kw : item->MetaData().keywords) {
            ss << pad << L"            <Keyword>" << EscapeXml(kw) << L"</Keyword>\n";
        }
        ss << pad << L"        </Keywords>\n";
    }
    ss << pad << L"    </MetaData>\n";

    // Target
    if (item->MetaData().targetWords > 0) {
        ss << pad << L"    <TextSettings>\n";
        ss << pad << L"        <Target Type=\"Words\" Maximum=\"" << item->MetaData().targetWords << L"\"/>\n";
        ss << pad << L"    </TextSettings>\n";
    }

    // Children
    ss << pad << L"    <Children>\n";
    for (const auto& child : item->GetChildren()) {
        SerializeBinderItemXml(ss, child, indent + 2);
    }
    ss << pad << L"    </Children>\n";

    ss << pad << L"</BinderItem>\n";
}

} // namespace

bool ProjectEngine::SerializeMasterXml() {
    std::wstringstream ss;
    ss << L"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
    ss << L"<ScrivenerProject Version=\"3.0\" Creator=\"Escritorio-1.0\" Device=\"Windows-11\" Modified=\""
       << GetCurrentIsoTimestamp() << L"\">\n";

    ss << L"    <ProjectIdentifier>" << m_identifier << L"</ProjectIdentifier>\n";
    ss << L"    <ProjectTitle>" << EscapeXml(m_title) << L"</ProjectTitle>\n";

    // Binder
    ss << L"    <Binder>\n";
    for (const auto& root : m_rootItems) {
        SerializeBinderItemXml(ss, root, 2);
    }
    ss << L"    </Binder>\n";

    // Labels
    ss << L"    <LabelSettings>\n";
    ss << L"        <Title>Etiqueta</Title>\n";
    ss << L"        <Labels>\n";
    for (const auto& [id, lbl] : m_labels) {
        ss << L"            <Label ID=\"" << id << L"\" Color=\"" << lbl.colorRgba << L"\">" << EscapeXml(lbl.name) << L"</Label>\n";
    }
    ss << L"        </Labels>\n";
    ss << L"    </LabelSettings>\n";

    // Statuses
    ss << L"    <StatusSettings>\n";
    ss << L"        <Title>Estado</Title>\n";
    ss << L"        <Statuses>\n";
    for (const auto& [id, st] : m_statuses) {
        ss << L"            <Status ID=\"" << id << L"\">" << EscapeXml(st.name) << L"</Status>\n";
    }
    ss << L"        </Statuses>\n";
    ss << L"    </StatusSettings>\n";

    // Section Types
    ss << L"    <SectionTypes>\n";
    for (const auto& [id, name] : m_sectionTypes) {
        ss << L"        <Type ID=\"" << EscapeXml(id) << L"\">" << EscapeXml(name) << L"</Type>\n";
    }
    ss << L"    </SectionTypes>\n";

    // Project Targets
    ss << L"    <ProjectTargets>\n";
    ss << L"        <DraftTarget Type=\"Words\" Count=\"" << m_draftTargetWords << L"\"/>\n";
    ss << L"        <SessionTarget Type=\"Words\" Count=\"" << m_sessionTargetWords << L"\"/>\n";
    ss << L"    </ProjectTargets>\n";

    // Collections
    ss << L"    <Collections>\n";
    for (const auto& col : m_collections) {
        std::wstring colType = (col.type == CollectionType::Search) ? L"Search" : L"Arbitrary";
        ss << L"        <Collection ID=\"" << EscapeXml(col.id) << L"\" Type=\"" << colType << L"\">\n";
        ss << L"            <Title>" << EscapeXml(col.title) << L"</Title>\n";
        if (col.type == CollectionType::Search) {
            ss << L"            <Query>" << EscapeXml(col.searchQuery) << L"</Query>\n";
        } else {
            ss << L"            <Items>\n";
            for (const auto& uuid : col.itemUuids) {
                ss << L"                <Item UUID=\"" << uuid << L"\"/>\n";
            }
            ss << L"            </Items>\n";
        }
        ss << L"        </Collection>\n";
    }
    ss << L"    </Collections>\n";

    ss << L"</ScrivenerProject>\n";

    // Escritura atómica a disco
    std::string utf8Data = WideToUtf8(ss.str());
    auto targetPath = GetMasterXmlPath();
    std::wstring tmpPath = targetPath.wstring() + L".tmp";

    HANDLE hFile = CreateFileW(tmpPath.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (hFile == INVALID_HANDLE_VALUE) return false;

    DWORD written = 0;
    WriteFile(hFile, utf8Data.data(), static_cast<DWORD>(utf8Data.size()), &written, nullptr);
    FlushFileBuffers(hFile);
    CloseHandle(hFile);

    MoveFileExW(tmpPath.c_str(), targetPath.wstring().c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH);
    return true;
}

bool ProjectEngine::ParseMasterXml() {
    auto targetPath = GetMasterXmlPath();
    if (!std::filesystem::exists(targetPath)) {
        // Probar buscando cualquier archivo .scrivx o .escrx en la raíz
        for (const auto& entry : std::filesystem::directory_iterator(m_projectPath)) {
            if (entry.path().extension() == L".scrivx" || entry.path().extension() == L".escrx") {
                targetPath = entry.path();
                break;
            }
        }
        if (!std::filesystem::exists(targetPath)) return false;
    }

    std::ifstream file(targetPath, std::ios::binary);
    if (!file.is_open()) return false;

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::wstring xml = Utf8ToWide(buffer.str());

    // Extracción de título
    auto tStart = xml.find(L"<ProjectTitle>");
    if (tStart != std::wstring::npos) {
        tStart += 14;
        auto tEnd = xml.find(L"</ProjectTitle>", tStart);
        if (tEnd != std::wstring::npos) {
            m_title = xml.substr(tStart, tEnd - tStart);
        }
    }

    // Extracción de identificador
    auto idStart = xml.find(L"<ProjectIdentifier>");
    if (idStart != std::wstring::npos) {
        idStart += 19;
        auto idEnd = xml.find(L"</ProjectIdentifier>", idStart);
        if (idEnd != std::wstring::npos) {
            m_identifier = xml.substr(idStart, idEnd - idStart);
        }
    }

    // Extracción simple de BinderItems
    m_rootItems.clear();
    size_t pos = 0;
    while ((pos = xml.find(L"<BinderItem ", pos)) != std::wstring::npos) {
        // UUID
        auto uStart = xml.find(L"UUID=\"", pos);
        if (uStart == std::wstring::npos || uStart > pos + 100) { pos += 12; continue; }
        uStart += 6;
        auto uEnd = xml.find(L"\"", uStart);
        std::wstring uuid = xml.substr(uStart, uEnd - uStart);

        // Type
        auto typeStart = xml.find(L"Type=\"", pos);
        std::wstring typeStr = L"Text";
        if (typeStart != std::wstring::npos && typeStart < uEnd + 100) {
            typeStart += 6;
            auto typeEnd = xml.find(L"\"", typeStart);
            typeStr = xml.substr(typeStart, typeEnd - typeStart);
        }

        // Title
        auto titleStart = xml.find(L"<Title>", pos);
        std::wstring title = L"Sin Título";
        if (titleStart != std::wstring::npos && titleStart < pos + 300) {
            titleStart += 7;
            auto titleEnd = xml.find(L"</Title>", titleStart);
            title = xml.substr(titleStart, titleEnd - titleStart);
        }

        auto item = std::make_shared<BinderItem>(uuid, StringToBinderType(typeStr), title, this);
        m_rootItems.push_back(item);
        pos = uEnd;
    }

    // Si no se extrajeron raíces pero el proyecto está bien, asegurar las 3 raíces básicas
    if (m_rootItems.empty()) {
        m_rootItems.push_back(std::make_shared<BinderItem>(GenerateUuid(), BinderItemType::DraftFolder, L"Manuscrito", this));
        m_rootItems.push_back(std::make_shared<BinderItem>(GenerateUuid(), BinderItemType::ResearchFolder, L"Investigación", this));
        m_rootItems.push_back(std::make_shared<BinderItem>(GenerateUuid(), BinderItemType::TrashFolder, L"Papelera", this));
    }

    return true;
}

} // namespace escritorio::core
