#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <chrono>
#include <filesystem>
#include <optional>

namespace escritorio::core {

// Tipos de elementos de Binder según estándar Scrivener 3 y Escritorio
enum class BinderItemType {
    DraftFolder,
    ResearchFolder,
    TrashFolder,
    Folder,
    Text,
    PDF,
    Image,
    Media,
    WebArchive
};

// Conversión de tipos
std::wstring BinderTypeToString(BinderItemType type);
BinderItemType StringToBinderType(const std::wstring& str);

// Estructura de Metadatos de un nodo
struct ItemMetaData {
    bool includeInCompile = true;
    std::wstring sectionType = L"Structure Based";
    int targetWords = 0;
    int statusId = -1;
    int labelId = -1;
    std::wstring fileExtension = L"rtf";
    std::wstring iconFileName = L"";
    std::map<std::wstring, std::wstring> customMetaData;
    std::vector<std::wstring> keywords;
};

// Definición de etiquetas cromáticas
struct LabelInfo {
    int id = -1;
    std::wstring name;
    std::wstring colorRgba = L"1.0 1.0 1.0 1.0";
};

// Definición de estados
struct StatusInfo {
    int id = -1;
    std::wstring name;
};

// Definición de Colecciones
enum class CollectionType {
    Arbitrary,
    Search
};

struct CollectionInfo {
    std::wstring id;
    std::wstring title;
    CollectionType type = CollectionType::Arbitrary;
    std::vector<std::wstring> itemUuids;
    std::wstring searchQuery;
};

class ProjectEngine;

/**
 * @brief Nodo jerárquico del Binder con soporte para carga diferida (Lazy Loading)
 * y persistencia transaccional atómica en Files/Data/<UUID>/.
 */
class BinderItem : public std::enable_shared_from_this<BinderItem> {
public:
    BinderItem(const std::wstring& uuid, BinderItemType type, const std::wstring& title, ProjectEngine* engine);

    const std::wstring& GetUuid() const { return m_uuid; }
    BinderItemType GetType() const { return m_type; }
    void SetType(BinderItemType type) { m_type = type; m_modified = true; }

    const std::wstring& GetTitle() const { return m_title; }
    void SetTitle(const std::wstring& title) { m_title = title; m_modified = true; }

    const std::wstring& GetCreated() const { return m_created; }
    void SetCreated(const std::wstring& created) { m_created = created; }

    const std::wstring& GetModified() const { return m_modifiedDate; }
    void SetModified(const std::wstring& mod) { m_modifiedDate = mod; }

    ItemMetaData& MetaData() { m_modified = true; return m_metaData; }
    const ItemMetaData& MetaData() const { return m_metaData; }

    // Árbol jerárquico
    std::shared_ptr<BinderItem> GetParent() const { return m_parent.lock(); }
    void SetParent(std::shared_ptr<BinderItem> parent) { m_parent = parent; }

    const std::vector<std::shared_ptr<BinderItem>>& GetChildren() const { return m_children; }
    void AddChild(std::shared_ptr<BinderItem> child);
    bool RemoveChild(const std::wstring& uuid);
    std::shared_ptr<BinderItem> FindDescendant(const std::wstring& uuid);

    // Carga diferida (Lazy Loading) de recursos en Files/Data/<UUID>/
    std::string GetContentRtf();
    void SetContentRtf(const std::string& rtf);

    std::string GetSynopsis();
    void SetSynopsis(const std::string& synopsis);

    std::string GetNotesRtf();
    void SetNotesRtf(const std::string& notes);

    std::string GetCommentsXml();
    void SetCommentsXml(const std::string& comments);

    // Estado sucio y guardado atómico
    bool IsDirty() const { return m_isDirty; }
    std::chrono::steady_clock::time_point GetLastModifiedTime() const { return m_lastModifiedTime; }
    bool SaveIfDirty();

private:
    std::filesystem::path GetDataDirectory() const;
    bool WriteAtomicFile(const std::filesystem::path& targetFile, const std::string& data);

    std::wstring m_uuid;
    BinderItemType m_type;
    std::wstring m_title;
    std::wstring m_created;
    std::wstring m_modifiedDate;
    ItemMetaData m_metaData;

    std::weak_ptr<BinderItem> m_parent;
    std::vector<std::shared_ptr<BinderItem>> m_children;

    // Cachés de carga diferida
    std::optional<std::string> m_contentRtf;
    std::optional<std::string> m_synopsis;
    std::optional<std::string> m_notesRtf;
    std::optional<std::string> m_commentsXml;

    bool m_isDirty = false;
    bool m_modified = false;
    std::chrono::steady_clock::time_point m_lastModifiedTime;

    ProjectEngine* m_engine = nullptr;
};

/**
 * @brief Información del cerrojo de concurrencia project.lock.
 */
struct ProjectLockInfo {
    DWORD pid = 0;
    std::wstring hostname;
    std::wstring username;
    std::wstring timestamp;
};

/**
 * @brief Motor Principal de Proyectos de Escritorio y Scrivener 3.
 * 
 * Gestiona el ciclo de vida completo de paquetes .escr y .scriv:
 * - Parsing y serialización XML de .escrx y .scrivx
 * - Concurrencia segura mediante project.lock
 * - Carga diferida de documentos
 * - Autoguardado atómico transaccional (FlushFileBuffers + MoveFileExW)
 */
class ProjectEngine {
public:
    ProjectEngine();
    ~ProjectEngine();

    // Creación y Carga de Proyectos
    static std::shared_ptr<ProjectEngine> CreateNew(const std::wstring& directoryPath, const std::wstring& title, bool isNative = true);
    static std::shared_ptr<ProjectEngine> Open(const std::wstring& directoryPath, bool forceUnlock = false);

    bool Save();
    void Close();

    // Formato y rutas
    bool IsNative() const { return m_isNative; }
    const std::filesystem::path& GetProjectPath() const { return m_projectPath; }
    std::filesystem::path GetMasterXmlPath() const;

    // Control de Bloqueo Concurrente (project.lock)
    bool IsLocked(ProjectLockInfo* outInfo = nullptr) const;
    bool AcquireLock();
    void ReleaseLock();

    // Metadatos globales del proyecto
    const std::wstring& GetIdentifier() const { return m_identifier; }
    const std::wstring& GetTitle() const { return m_title; }
    void SetTitle(const std::wstring& title) { m_title = title; m_isDirty = true; }

    int GetDraftTargetWords() const { return m_draftTargetWords; }
    void SetDraftTargetWords(int count) { m_draftTargetWords = count; m_isDirty = true; }

    int GetSessionTargetWords() const { return m_sessionTargetWords; }
    void SetSessionTargetWords(int count) { m_sessionTargetWords = count; m_isDirty = true; }

    // Árbol del Binder
    std::shared_ptr<BinderItem> GetRootItem(size_t index) const;
    size_t GetRootItemCount() const { return m_rootItems.size(); }
    std::shared_ptr<BinderItem> FindItem(const std::wstring& uuid) const;
    std::shared_ptr<BinderItem> AddItem(const std::wstring& parentUuid, const std::wstring& title, BinderItemType type);

    // Etiquetas, Estados y Tipos de Sección
    const std::map<int, LabelInfo>& GetLabels() const { return m_labels; }
    void SetLabel(int id, const std::wstring& name, const std::wstring& colorRgba);

    const std::map<int, StatusInfo>& GetStatuses() const { return m_statuses; }
    void SetStatus(int id, const std::wstring& name);

    const std::map<std::wstring, std::wstring>& GetSectionTypes() const { return m_sectionTypes; }
    void SetSectionType(const std::wstring& id, const std::wstring& name);

    // Colecciones
    const std::vector<CollectionInfo>& GetCollections() const { return m_collections; }
    void AddCollection(const CollectionInfo& col) { m_collections.push_back(col); m_isDirty = true; }

    // Motor de Autoguardado Atómico (2 segundos de inactividad)
    int AutosavePendingChanges(int inactivityThresholdMs = 2000);

private:
    bool ParseMasterXml();
    bool SerializeMasterXml();
    std::shared_ptr<BinderItem> ParseBinderItemNode(void* xmlNode);

    std::filesystem::path m_projectPath;
    bool m_isNative = true;
    bool m_isDirty = false;
    bool m_hasLock = false;

    std::wstring m_identifier;
    std::wstring m_title;
    int m_draftTargetWords = 50000;
    int m_sessionTargetWords = 1500;

    std::vector<std::shared_ptr<BinderItem>> m_rootItems;
    std::map<int, LabelInfo> m_labels;
    std::map<int, StatusInfo> m_statuses;
    std::map<std::wstring, std::wstring> m_sectionTypes;
    std::vector<CollectionInfo> m_collections;
};

} // namespace escritorio::core
