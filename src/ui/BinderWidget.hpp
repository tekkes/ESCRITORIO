#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include "../themes/ThemeEngine.hpp"

namespace escritorio::ui {

enum class BinderItemType {
    DraftFolder,
    ResearchFolder,
    TrashFolder,
    TemplatesFolder,
    Folder,
    Text,
    PDF,
    Image,
    Media,
    WebArchive
};

enum class BinderLabelColorMode {
    None,
    DotRight,
    IconTint,
    RowHighlight
};

struct BinderNode {
    std::wstring uuid;
    std::wstring title;
    BinderItemType type = BinderItemType::Text;
    int depth = 0;
    bool isExpanded = true;
    bool isSelected = false;
    COLORREF labelColor = RGB(0, 0, 0);
    bool hasLabelColor = false;
    COLORREF statusColor = RGB(16, 185, 129);
    std::wstring iconId;
    std::wstring textContent; // Capacidad dual: carpetas pueden almacenar texto
    std::vector<std::shared_ptr<BinderNode>> children;
    std::weak_ptr<BinderNode> parent;
};

struct CollectionTab {
    std::wstring id;
    std::wstring title;
    bool isSearch = false;
    std::wstring searchQuery;
    COLORREF tabColor = RGB(99, 102, 241);
    std::vector<std::wstring> itemUuids;
};

class BinderWidget {
public:
    BinderWidget();
    ~BinderWidget() = default;

    void InitDefaultTree();

    // Navegación y Colecciones
    int GetActiveTabIndex() const { return m_activeTabIndex; }
    void SetActiveTabIndex(int idx);
    void AddStandardCollection(const std::wstring& title, COLORREF color);
    void AddSearchCollection(const std::wstring& title, const std::wstring& query, COLORREF color);
    const std::vector<CollectionTab>& GetCollections() const { return m_collections; }

    // Capacidad dual y operaciones de estructura narrativa
    bool GroupSelection(const std::wstring& folderTitle = L"Nueva Carpeta");
    bool UngroupSelection();
    bool SplitSelection(size_t splitPos, const std::wstring& newTitle = L"Continuación");
    bool MergeSelection();
    bool DuplicateSelection();
    bool TrashSelection();
    bool RestoreSelection();

    // Personalización visual
    void SetLabelColorMode(BinderLabelColorMode mode) { m_labelMode = mode; }
    BinderLabelColorMode GetLabelColorMode() const { return m_labelMode; }
    void SetNodeIcon(const std::wstring& uuid, const std::wstring& iconId);

    // Selección
    void SelectNode(const std::wstring& uuid, bool extend = false);
    const std::vector<std::wstring>& GetSelectedUuids() const { return m_selectedUuids; }
    std::shared_ptr<BinderNode> GetNode(const std::wstring& uuid) const;

    // Renderizado en DC
    void Render(HDC hdc, const RECT& bounds, const escritorio::themes::ThemePalette& pal,
                const escritorio::themes::UIDensityMetrics& metrics);

    // Búsqueda y evaluación en tiempo real
    std::vector<std::shared_ptr<BinderNode>> EvaluateSearch(const std::wstring& query) const;

private:
    std::shared_ptr<BinderNode> FindNodeRecursive(const std::shared_ptr<BinderNode>& current, const std::wstring& uuid) const;
    void FlattenVisibleNodes(const std::shared_ptr<BinderNode>& current, std::vector<std::shared_ptr<BinderNode>>& outList) const;

    std::vector<std::shared_ptr<BinderNode>> m_rootNodes;
    std::vector<std::wstring> m_selectedUuids;
    std::vector<CollectionTab> m_collections;
    int m_activeTabIndex = 0; // 0 = Cuaderno completo
    BinderLabelColorMode m_labelMode = BinderLabelColorMode::DotRight;

    std::shared_ptr<BinderNode> m_draftFolder;
    std::shared_ptr<BinderNode> m_researchFolder;
    std::shared_ptr<BinderNode> m_trashFolder;
    std::shared_ptr<BinderNode> m_templatesFolder;
};

} // namespace escritorio::ui
