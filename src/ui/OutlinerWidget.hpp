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

struct NativeOutlinerColumn {
    std::wstring id;
    std::wstring title;
    int width = 120;
    int minWidth = 50;
    bool visible = true;
};

struct NativeOutlinerItem {
    std::wstring uuid;
    std::wstring title;
    std::wstring synopsis;
    int level = 0;
    bool expanded = true;
    bool isFolder = false;

    // Métricas
    int words = 0;
    int totalWords = 0;
    int characters = 0;
    int totalCharacters = 0;
    int target = 0;
    int totalTarget = 0;
    float progressPercent = 0.0f;

    // Metadatos
    bool includeInCompile = true;
    std::wstring sectionType = L"Structure Based";
    int labelId = -1;
    std::wstring labelName = L"Sin Etiqueta";
    COLORREF labelColor = RGB(148, 163, 184);

    int statusId = -1;
    std::wstring statusName = L"Borrador";

    std::wstring created = L"2026-10-22";
    std::wstring modified = L"2026-10-22";
    std::vector<std::wstring> keywords;
    std::map<std::wstring, std::wstring> customMetadata;
};

enum class OutlinerSortDirection {
    None,
    Ascending,
    Descending
};

class OutlinerWidget {
public:
    OutlinerWidget();
    ~OutlinerWidget() = default;

    void Clear();
    void AddItem(const NativeOutlinerItem& item);
    size_t GetItemCount() const { return m_items.size(); }
    NativeOutlinerItem* GetItem(size_t index);
    NativeOutlinerItem* GetItemByUuid(const std::wstring& uuid);

    // Configuración de visualización
    void SetCombinedTitleSynopsis(bool combined) { m_combinedTitleSynopsis = combined; }
    bool IsCombinedTitleSynopsis() const { return m_combinedTitleSynopsis; }

    void SetFilterQuery(const std::wstring& query) { m_filterQuery = query; }
    const std::wstring& GetFilterQuery() const { return m_filterQuery; }

    void SetSort(const std::wstring& colId, OutlinerSortDirection dir);
    void CycleSort(const std::wstring& colId);

    // Exportación
    std::wstring ExportToCsvString() const;

    // Columnas
    std::vector<NativeOutlinerColumn>& GetColumns() { return m_columns; }
    const std::vector<NativeOutlinerColumn>& GetColumns() const { return m_columns; }
    void ToggleColumn(const std::wstring& colId);

    // Renderizado en HDC
    void Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                const escritorio::themes::UIDensityMetrics& metrics, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);

    static COLORREF CalculateProgressColor(float percent);

private:
    std::vector<NativeOutlinerItem> m_items;
    std::vector<NativeOutlinerColumn> m_columns;

    bool m_combinedTitleSynopsis = true;
    std::wstring m_sortColId;
    OutlinerSortDirection m_sortDir = OutlinerSortDirection::None;
    std::wstring m_filterQuery;

    int m_rowHeight = 38;
    int m_headerHeight = 26;
    int m_scrollOffset = 0;

    void RenderHeader(HDC hdc, const RECT& headerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall);
    void RenderRow(HDC hdc, const RECT& rowRect, const NativeOutlinerItem& item, bool isSelected,
                   const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderProgressBar(HDC hdc, const RECT& barRect, float percent, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall);
    void RenderFooter(HDC hdc, const RECT& footerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall);
};

} // namespace escritorio::ui
