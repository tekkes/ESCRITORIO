#include "BinderWidget.hpp"
#include <algorithm>

namespace escritorio::ui {

BinderWidget::BinderWidget() {
    InitDefaultTree();
}

void BinderWidget::InitDefaultTree() {
    m_rootNodes.clear();

    // 1. Manuscrito (Draft)
    m_draftFolder = std::make_shared<BinderNode>();
    m_draftFolder->uuid = L"draft-folder-uuid";
    m_draftFolder->title = L"Manuscrito";
    m_draftFolder->type = BinderItemType::DraftFolder;
    m_draftFolder->isExpanded = true;
    m_draftFolder->statusColor = RGB(59, 130, 246);

    // Subcarpetas y escenas de ejemplo
    auto cap1 = std::make_shared<BinderNode>();
    cap1->uuid = L"chapter-1-uuid";
    cap1->title = L"Cap. 1: El Despertar";
    cap1->type = BinderItemType::Folder;
    cap1->isExpanded = true;
    cap1->statusColor = RGB(234, 88, 12);
    cap1->parent = m_draftFolder;

    auto esc1 = std::make_shared<BinderNode>();
    esc1->uuid = L"scene-1-1-uuid";
    esc1->title = L"Escena 1.1: La Niebla";
    esc1->type = BinderItemType::Text;
    esc1->statusColor = RGB(16, 185, 129);
    esc1->labelColor = RGB(59, 130, 246);
    esc1->hasLabelColor = true;
    esc1->textContent = L"La noche caía sobre las torres antiguas...";
    esc1->parent = cap1;

    auto esc2 = std::make_shared<BinderNode>();
    esc2->uuid = L"scene-1-2-uuid";
    esc2->title = L"Escena 1.2: El Umbral";
    esc2->type = BinderItemType::Text;
    esc2->statusColor = RGB(239, 68, 68);
    esc2->labelColor = RGB(234, 88, 12);
    esc2->hasLabelColor = true;
    esc2->parent = cap1;

    cap1->children.push_back(esc1);
    cap1->children.push_back(esc2);

    auto cap2 = std::make_shared<BinderNode>();
    cap2->uuid = L"chapter-2-uuid";
    cap2->title = L"Cap. 2: La Ciudad";
    cap2->type = BinderItemType::Folder;
    cap2->statusColor = RGB(156, 163, 175);
    cap2->parent = m_draftFolder;

    m_draftFolder->children.push_back(cap1);
    m_draftFolder->children.push_back(cap2);

    // 2. Investigación (Research)
    m_researchFolder = std::make_shared<BinderNode>();
    m_researchFolder->uuid = L"research-folder-uuid";
    m_researchFolder->title = L"Investigación";
    m_researchFolder->type = BinderItemType::ResearchFolder;
    m_researchFolder->statusColor = RGB(16, 185, 129);

    auto note1 = std::make_shared<BinderNode>();
    note1->uuid = L"note-castillo-uuid";
    note1->title = L"Planos del Castillo";
    note1->type = BinderItemType::Text;
    note1->parent = m_researchFolder;
    m_researchFolder->children.push_back(note1);

    // 3. Plantillas (Templates)
    m_templatesFolder = std::make_shared<BinderNode>();
    m_templatesFolder->uuid = L"templates-folder-uuid";
    m_templatesFolder->title = L"Plantillas";
    m_templatesFolder->type = BinderItemType::TemplatesFolder;
    m_templatesFolder->statusColor = RGB(139, 92, 246);

    auto tpl1 = std::make_shared<BinderNode>();
    tpl1->uuid = L"tpl-char-uuid";
    tpl1->title = L"Ficha de Personaje";
    tpl1->type = BinderItemType::Text;
    tpl1->parent = m_templatesFolder;
    m_templatesFolder->children.push_back(tpl1);

    // 4. Papelera (Trash)
    m_trashFolder = std::make_shared<BinderNode>();
    m_trashFolder->uuid = L"trash-folder-uuid";
    m_trashFolder->title = L"Papelera";
    m_trashFolder->type = BinderItemType::TrashFolder;
    m_trashFolder->statusColor = RGB(239, 68, 68);

    m_rootNodes.push_back(m_draftFolder);
    m_rootNodes.push_back(m_researchFolder);
    m_rootNodes.push_back(m_templatesFolder);
    m_rootNodes.push_back(m_trashFolder);

    // Colecciones por defecto
    CollectionTab col1;
    col1.id = L"col-characters";
    col1.title = L"Personajes";
    col1.isSearch = false;
    col1.tabColor = RGB(168, 85, 247);
    col1.itemUuids.push_back(esc1->uuid);
    m_collections.push_back(col1);

    CollectionTab col2;
    col2.id = L"col-pending-search";
    col2.title = L"Pendientes (Búsqueda)";
    col2.isSearch = true;
    col2.searchQuery = L"Umbral";
    col2.tabColor = RGB(234, 88, 12);
    m_collections.push_back(col2);

    m_selectedUuids.push_back(esc1->uuid);
}

void BinderWidget::SetActiveTabIndex(int idx) {
    if (idx >= 0 && idx <= static_cast<int>(m_collections.size())) {
        m_activeTabIndex = idx;
    }
}

void BinderWidget::AddStandardCollection(const std::wstring& title, COLORREF color) {
    CollectionTab col;
    col.id = L"col-" + std::to_wstring(m_collections.size() + 1);
    col.title = title;
    col.isSearch = false;
    col.tabColor = color;
    m_collections.push_back(col);
}

void BinderWidget::AddSearchCollection(const std::wstring& title, const std::wstring& query, COLORREF color) {
    CollectionTab col;
    col.id = L"col-search-" + std::to_wstring(m_collections.size() + 1);
    col.title = title;
    col.isSearch = true;
    col.searchQuery = query;
    col.tabColor = color;
    m_collections.push_back(col);
}

std::shared_ptr<BinderNode> BinderWidget::FindNodeRecursive(const std::shared_ptr<BinderNode>& current, const std::wstring& uuid) const {
    if (!current) return nullptr;
    if (current->uuid == uuid) return current;
    for (const auto& child : current->children) {
        auto found = FindNodeRecursive(child, uuid);
        if (found) return found;
    }
    return nullptr;
}

std::shared_ptr<BinderNode> BinderWidget::GetNode(const std::wstring& uuid) const {
    for (const auto& root : m_rootNodes) {
        auto found = FindNodeRecursive(root, uuid);
        if (found) return found;
    }
    return nullptr;
}

void BinderWidget::SelectNode(const std::wstring& uuid, bool extend) {
    if (!extend) {
        m_selectedUuids.clear();
    }
    if (std::find(m_selectedUuids.begin(), m_selectedUuids.end(), uuid) == m_selectedUuids.end()) {
        m_selectedUuids.push_back(uuid);
    }
}

void BinderWidget::SetNodeIcon(const std::wstring& uuid, const std::wstring& iconId) {
    auto node = GetNode(uuid);
    if (node) {
        node->iconId = iconId;
    }
}

bool BinderWidget::GroupSelection(const std::wstring& folderTitle) {
    if (m_selectedUuids.empty()) return false;
    auto first = GetNode(m_selectedUuids[0]);
    if (!first) return false;

    auto parent = first->parent.lock();
    if (!parent) return false;

    auto newFolder = std::make_shared<BinderNode>();
    newFolder->uuid = L"folder-" + std::to_wstring(rand());
    newFolder->title = folderTitle;
    newFolder->type = BinderItemType::Folder;
    newFolder->isExpanded = true;
    newFolder->parent = parent;

    // Mover elementos seleccionados
    for (const auto& u : m_selectedUuids) {
        auto it = GetNode(u);
        if (it && it->type != BinderItemType::DraftFolder && it->type != BinderItemType::ResearchFolder && it->type != BinderItemType::TrashFolder) {
            auto oldP = it->parent.lock();
            if (oldP) {
                auto& ch = oldP->children;
                ch.erase(std::remove(ch.begin(), ch.end(), it), ch.end());
            }
            it->parent = newFolder;
            newFolder->children.push_back(it);
        }
    }

    parent->children.push_back(newFolder);
    m_selectedUuids = { newFolder->uuid };
    return true;
}

bool BinderWidget::UngroupSelection() {
    if (m_selectedUuids.empty()) return false;
    auto node = GetNode(m_selectedUuids[0]);
    if (!node || node->type == BinderItemType::DraftFolder || node->type == BinderItemType::ResearchFolder || node->type == BinderItemType::TrashFolder) {
        return false;
    }

    auto parent = node->parent.lock();
    if (!parent) return false;

    for (auto& child : node->children) {
        child->parent = parent;
        parent->children.push_back(child);
    }
    node->children.clear();

    auto& pChildren = parent->children;
    pChildren.erase(std::remove(pChildren.begin(), pChildren.end(), node), pChildren.end());
    return true;
}

bool BinderWidget::SplitSelection(size_t splitPos, const std::wstring& newTitle) {
    if (m_selectedUuids.empty()) return false;
    auto node = GetNode(m_selectedUuids[0]);
    if (!node) return false;

    auto parent = node->parent.lock();
    if (!parent) return false;

    std::wstring firstText = node->textContent.substr(0, (std::min)(splitPos, node->textContent.length()));
    std::wstring secondText = (splitPos < node->textContent.length()) ? node->textContent.substr(splitPos) : L"";

    node->textContent = firstText;

    auto newNode = std::make_shared<BinderNode>();
    newNode->uuid = L"doc-split-" + std::to_wstring(rand());
    newNode->title = newTitle;
    newNode->type = node->type;
    newNode->textContent = secondText;
    newNode->parent = parent;

    parent->children.push_back(newNode);
    m_selectedUuids = { newNode->uuid };
    return true;
}

bool BinderWidget::MergeSelection() {
    if (m_selectedUuids.size() < 2) return false;
    auto primary = GetNode(m_selectedUuids[0]);
    if (!primary) return false;

    for (size_t i = 1; i < m_selectedUuids.size(); ++i) {
        auto other = GetNode(m_selectedUuids[i]);
        if (!other) continue;
        if (!other->textContent.empty()) {
            primary->textContent += L"\n\n* * *\n\n" + other->textContent;
        }
        for (auto& ch : other->children) {
            ch->parent = primary;
            primary->children.push_back(ch);
        }
        other->children.clear();

        auto oldP = other->parent.lock();
        if (oldP) {
            auto& ch = oldP->children;
            ch.erase(std::remove(ch.begin(), ch.end(), other), ch.end());
        }
    }
    return true;
}

bool BinderWidget::DuplicateSelection() {
    if (m_selectedUuids.empty()) return false;
    auto src = GetNode(m_selectedUuids[0]);
    if (!src) return false;

    auto parent = src->parent.lock();
    if (!parent) return false;

    auto clone = std::make_shared<BinderNode>();
    clone->uuid = src->uuid + L"-copy-" + std::to_wstring(rand());
    clone->title = src->title + L" (Copia)";
    clone->type = src->type;
    clone->labelColor = src->labelColor;
    clone->hasLabelColor = src->hasLabelColor;
    clone->statusColor = src->statusColor;
    clone->textContent = src->textContent;
    clone->parent = parent;

    parent->children.push_back(clone);
    m_selectedUuids = { clone->uuid };
    return true;
}

bool BinderWidget::TrashSelection() {
    if (m_selectedUuids.empty() || !m_trashFolder) return false;
    for (const auto& u : m_selectedUuids) {
        auto node = GetNode(u);
        if (node && node->type != BinderItemType::DraftFolder && node->type != BinderItemType::ResearchFolder && node->type != BinderItemType::TrashFolder) {
            auto parent = node->parent.lock();
            if (parent) {
                auto& ch = parent->children;
                ch.erase(std::remove(ch.begin(), ch.end(), node), ch.end());
            }
            node->parent = m_trashFolder;
            m_trashFolder->children.push_back(node);
        }
    }
    m_selectedUuids.clear();
    return true;
}

bool BinderWidget::RestoreSelection() {
    if (m_selectedUuids.empty() || !m_draftFolder) return false;
    for (const auto& u : m_selectedUuids) {
        auto node = GetNode(u);
        if (node) {
            auto parent = node->parent.lock();
            if (parent && parent == m_trashFolder) {
                auto& ch = m_trashFolder->children;
                ch.erase(std::remove(ch.begin(), ch.end(), node), ch.end());
                node->parent = m_draftFolder;
                m_draftFolder->children.push_back(node);
            }
        }
    }
    return true;
}

std::vector<std::shared_ptr<BinderNode>> BinderWidget::EvaluateSearch(const std::wstring& query) const {
    std::vector<std::shared_ptr<BinderNode>> matches;
    if (query.empty()) return matches;

    std::wstring qLower = query;
    std::transform(qLower.begin(), qLower.end(), qLower.begin(), ::towlower);

    auto searchNode = [&](auto& self, const std::shared_ptr<BinderNode>& node) -> void {
        if (!node) return;
        std::wstring tLower = node->title;
        std::transform(tLower.begin(), tLower.end(), tLower.begin(), ::towlower);
        if (tLower.find(qLower) != std::wstring::npos) {
            matches.push_back(node);
        }
        for (const auto& c : node->children) {
            self(self, c);
        }
    };

    for (const auto& r : m_rootNodes) {
        if (r->type != BinderItemType::TrashFolder) {
            searchNode(searchNode, r);
        }
    }
    return matches;
}

void BinderWidget::FlattenVisibleNodes(const std::shared_ptr<BinderNode>& current, std::vector<std::shared_ptr<BinderNode>>& outList) const {
    if (!current) return;
    outList.push_back(current);
    if (current->isExpanded) {
        for (const auto& child : current->children) {
            child->depth = current->depth + 1;
            FlattenVisibleNodes(child, outList);
        }
    }
}

void BinderWidget::Render(HDC hdc, const RECT& bounds, const escritorio::themes::ThemePalette& pal,
                          const escritorio::themes::UIDensityMetrics& metrics) {
    // 1. Fondo del panel
    HBRUSH hBrBg = CreateSolidBrush(pal.binderBg);
    FillRect(hdc, &bounds, hBrBg);
    DeleteObject(hBrBg);

    int top = bounds.top;
    int tabHeight = 22;

    // 2. Barra de Colecciones compacta en la parte superior
    RECT rcTabs = { bounds.left, top, bounds.right, top + tabHeight };
    HBRUSH hBrTabs = CreateSolidBrush(pal.toolbarBg);
    FillRect(hdc, &rcTabs, hBrTabs);
    DeleteObject(hBrTabs);

    SetBkMode(hdc, TRANSPARENT);

    // Pestaña Cuaderno
    bool isBinderTab = (m_activeTabIndex == 0);
    RECT rcTabBinder = { bounds.left + 4, top + 2, bounds.left + 70, top + tabHeight - 2 };
    if (isBinderTab) {
        HBRUSH hBrActive = CreateSolidBrush(pal.binderSelBg);
        FillRect(hdc, &rcTabBinder, hBrActive);
        DeleteObject(hBrActive);
        SetTextColor(hdc, pal.binderSelFg);
    } else {
        SetTextColor(hdc, pal.binderSecondary);
    }
    DrawTextW(hdc, L"Cuaderno", -1, &rcTabBinder, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    // Pestañas de Colecciones
    int tabX = bounds.left + 74;
    for (size_t i = 0; i < m_collections.size(); ++i) {
        bool isActive = (m_activeTabIndex == static_cast<int>(i + 1));
        RECT rcTab = { tabX, top + 2, tabX + 68, top + tabHeight - 2 };
        if (isActive) {
            HBRUSH hBrActive = CreateSolidBrush(m_collections[i].tabColor);
            FillRect(hdc, &rcTab, hBrActive);
            DeleteObject(hBrActive);
            SetTextColor(hdc, RGB(255, 255, 255));
        } else {
            SetTextColor(hdc, pal.binderSecondary);
        }
        DrawTextW(hdc, m_collections[i].title.c_str(), -1, &rcTab, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
        tabX += 72;
    }

    top += tabHeight + 4;

    // 3. Renderizado de lista: según sea Cuaderno completo o Colección activa
    std::vector<std::shared_ptr<BinderNode>> visibleNodes;

    if (m_activeTabIndex == 0) {
        // Árbol jerárquico multinivel
        for (const auto& root : m_rootNodes) {
            root->depth = 0;
            FlattenVisibleNodes(root, visibleNodes);
        }
    } else {
        // Colección activa
        size_t colIdx = m_activeTabIndex - 1;
        if (colIdx < m_collections.size()) {
            const auto& col = m_collections[colIdx];
            if (col.isSearch) {
                visibleNodes = EvaluateSearch(col.searchQuery);
            } else {
                for (const auto& u : col.itemUuids) {
                    auto it = GetNode(u);
                    if (it) visibleNodes.push_back(it);
                }
            }
        }
    }

    int rowHeight = metrics.binderRowHeight;
    for (const auto& node : visibleNodes) {
        if (top + rowHeight > bounds.bottom) break;

        bool isSelected = (std::find(m_selectedUuids.begin(), m_selectedUuids.end(), node->uuid) != m_selectedUuids.end());

        // Resaltado de selección o de etiqueta
        RECT rcRow = { bounds.left + 4, top, bounds.right - 4, top + rowHeight };
        if (isSelected) {
            HBRUSH hBrSel = CreateSolidBrush(pal.binderSelBg);
            FillRect(hdc, &rcRow, hBrSel);
            DeleteObject(hBrSel);
            SetTextColor(hdc, pal.binderSelFg);
        } else if (m_labelMode == BinderLabelColorMode::RowHighlight && node->hasLabelColor) {
            HBRUSH hBrLabel = CreateSolidBrush(RGB(
                (GetRValue(pal.binderBg) * 8 + GetRValue(node->labelColor) * 2) / 10,
                (GetGValue(pal.binderBg) * 8 + GetGValue(node->labelColor) * 2) / 10,
                (GetBValue(pal.binderBg) * 8 + GetBValue(node->labelColor) * 2) / 10
            ));
            FillRect(hdc, &rcRow, hBrLabel);
            DeleteObject(hBrLabel);
            SetTextColor(hdc, pal.binderFg);
        } else {
            SetTextColor(hdc, pal.binderFg);
        }

        // Indicador cromático de estado (6px circle)
        int dotX = bounds.left + 8 + (node->depth * 10);
        int dotY = top + (rowHeight - metrics.statusDotSize) / 2;

        HBRUSH hBrDot = CreateSolidBrush(node->statusColor);
        HPEN hNullPen = CreatePen(PS_NULL, 0, 0);
        HBRUSH hOldBr = static_cast<HBRUSH>(SelectObject(hdc, hBrDot));
        HPEN hOldPen = static_cast<HPEN>(SelectObject(hdc, hNullPen));
        Ellipse(hdc, dotX, dotY, dotX + metrics.statusDotSize, dotY + metrics.statusDotSize);
        SelectObject(hdc, hOldBr);
        SelectObject(hdc, hOldPen);
        DeleteObject(hBrDot);
        DeleteObject(hNullPen);

        // Texto del título
        RECT rcText = { dotX + metrics.statusDotSize + 6, top, bounds.right - 24, top + rowHeight };
        DrawTextW(hdc, node->title.c_str(), -1, &rcText, DT_LEFT | DT_VCENTER | DT_SINGLELINE);

        // Color de etiqueta a la derecha (DotRight)
        if (m_labelMode == BinderLabelColorMode::DotRight && node->hasLabelColor) {
            int lblDotX = bounds.right - 14;
            int lblDotY = top + (rowHeight - 6) / 2;
            HBRUSH hBrLbl = CreateSolidBrush(node->labelColor);
            HBRUSH hOld = static_cast<HBRUSH>(SelectObject(hdc, hBrLbl));
            Ellipse(hdc, lblDotX, lblDotY, lblDotX + 6, lblDotY + 6);
            SelectObject(hdc, hOld);
            DeleteObject(hBrLbl);
        }

        top += rowHeight;
    }
}

} // namespace escritorio::ui
