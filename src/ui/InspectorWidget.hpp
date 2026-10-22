#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <memory>
#include <map>
#include <chrono>
#include "../themes/ThemeEngine.hpp"

namespace escritorio::ui {

enum class NativeInspectorTab {
    NotesSynopsis = 0,    // 1. Sinopsis y Notas (conmutador texto/imagen + notes.rtf + label/status footer)
    Bookmarks = 1,        // 2. Marcadores (Doc / Proyecto + Visor previsualizador y editor)
    Metadata = 2,         // 3. Metadatos (Compile, Section Type, Custom Fields)
    Keywords = 3,         // 4. Palabras Clave (Keywords HUD flotante / jerárquico con colores)
    Snapshots = 4,        // 5. Instantáneas (Ctrl+5 / Ctrl+Shift+5, Myers Diff comparator, Rollback)
    CommentsFootnotes = 5 // 6. Comentarios interactivos y Notas al pie enlazadas a offsets
};

enum class NativeCustomFieldType {
    Text,
    Checkbox,
    List,
    Date
};

struct NativeCustomField {
    std::wstring name;
    NativeCustomFieldType type = NativeCustomFieldType::Text;
    std::wstring value;
    std::vector<std::wstring> listOptions;
};

struct NativeBookmarkItem {
    std::wstring id;
    std::wstring title;
    std::wstring pathOrUuid;
    bool isProjectLevel = false;
    std::wstring previewContent;
};

struct NativeSnapshotItem {
    std::wstring uuid;
    std::wstring title;
    std::wstring timestamp;
    std::wstring textContent;
};

enum class NativeDiffOp {
    Equal,
    Insert,
    Delete
};

struct NativeDiffSpan {
    NativeDiffOp op;
    std::wstring text;
};

struct NativeCommentItem {
    std::wstring id;
    bool isFootnote = false; // false = Comentario, true = Nota al pie
    std::wstring text;
    std::wstring author;
    std::wstring timestamp;
    COLORREF color = RGB(254, 240, 138); // Amarillo suave por defecto
    int startOffset = 0;
    int endOffset = 0;
};

class InspectorWidget {
public:
    InspectorWidget();
    ~InspectorWidget() = default;

    // Conmutación de pestañas (Cabecera 16px)
    NativeInspectorTab GetActiveTab() const { return m_activeTab; }
    void SetActiveTab(NativeInspectorTab tab) { m_activeTab = tab; }
    void CycleTab();

    // Sincronización de Documento
    void SetDocument(const std::wstring& uuid, const std::wstring& title);
    const std::wstring& GetDocumentUuid() const { return m_docUuid; }
    const std::wstring& GetDocumentTitle() const { return m_docTitle; }

    // Pestaña 1: Sinopsis y Notas
    bool IsSynopsisImageMode() const { return m_synopsisImageMode; }
    void ToggleSynopsisMode() { m_synopsisImageMode = !m_synopsisImageMode; }
    const std::wstring& GetSynopsisText() const { return m_synopsisText; }
    void SetSynopsisText(const std::wstring& text) { m_synopsisText = text; }
    const std::wstring& GetSynopsisImagePath() const { return m_synopsisImagePath; }
    void SetSynopsisImagePath(const std::wstring& path) { m_synopsisImagePath = path; }
    const std::wstring& GetNotesRtf() const { return m_notesRtf; }
    void SetNotesRtf(const std::wstring& rtf) { m_notesRtf = rtf; }

    // Pie fijo: Label y Status
    int GetLabelId() const { return m_labelId; }
    void SetLabel(int id, const std::wstring& name, COLORREF color);
    const std::wstring& GetLabelName() const { return m_labelName; }
    COLORREF GetLabelColor() const { return m_labelColor; }

    int GetStatusId() const { return m_statusId; }
    void SetStatus(int id, const std::wstring& name);
    const std::wstring& GetStatusName() const { return m_statusName; }

    // Pestaña 2: Marcadores
    bool IsProjectBookmarksScope() const { return m_bookmarkProjectScope; }
    void SetBookmarkScope(bool projectScope) { m_bookmarkProjectScope = projectScope; }
    void ToggleBookmarkScope() { m_bookmarkProjectScope = !m_bookmarkProjectScope; }
    void AddBookmark(const NativeBookmarkItem& bm);
    const std::vector<NativeBookmarkItem>& GetBookmarks() const { return m_bookmarks; }
    int GetSelectedBookmarkIndex() const { return m_selectedBookmarkIdx; }
    void SelectBookmark(int index);
    const std::wstring& GetBookmarkPreviewText() const { return m_bookmarkPreviewText; }
    void SetBookmarkPreviewText(const std::wstring& text);

    // Pestaña 3: Metadatos
    bool IsIncludeInCompile() const { return m_includeInCompile; }
    void SetIncludeInCompile(bool include) { m_includeInCompile = include; }
    const std::wstring& GetSectionType() const { return m_sectionType; }
    void SetSectionType(const std::wstring& st) { m_sectionType = st; }
    void AddCustomField(const NativeCustomField& field);
    std::vector<NativeCustomField>& GetCustomFields() { return m_customFields; }

    // Pestaña 4: Palabras clave y HUD
    bool IsKeywordsHudOpen() const { return m_isKeywordsHudOpen; }
    void ToggleKeywordsHud() { m_isKeywordsHudOpen = !m_isKeywordsHudOpen; }
    void AddKeyword(const std::wstring& kw, COLORREF color);
    const std::vector<std::pair<std::wstring, COLORREF>>& GetKeywords() const { return m_keywords; }

    // Pestaña 5: Instantáneas (Snapshots)
    void TakeSnapshot(const std::wstring& title = L"");
    const std::vector<NativeSnapshotItem>& GetSnapshots() const { return m_snapshots; }
    int GetSelectedSnapshotIndex() const { return m_selectedSnapshotIdx; }
    void SelectSnapshot(int index);
    void ComputeMyersDiff(int snapshotIndex, const std::wstring& currentDocText);
    const std::vector<NativeDiffSpan>& GetDiffSpans() const { return m_diffSpans; }
    bool Rollback(int snapshotIndex, bool takeSafetySnapshot, std::wstring& outRestoredText);

    // Pestaña 6: Comentarios y Notas al Pie
    void AddComment(const std::wstring& text, int startOffset, int endOffset, const std::wstring& author = L"Autor", COLORREF color = RGB(254, 240, 138));
    void AddFootnote(const std::wstring& text, int startOffset, int endOffset);
    const std::vector<NativeCommentItem>& GetComments() const { return m_comments; }
    int GetSelectedCommentIndex() const { return m_selectedCommentIdx; }
    void SelectComment(int index) { m_selectedCommentIdx = index; }
    int FindCommentAtOffset(int offset) const;

    // Manejo de eventos de ratón
    bool HandleClick(int x, int y, const RECT& inspectorRect);

    // Renderizado en HDC
    void Render(HDC hdc, const RECT& area, const escritorio::themes::ThemePalette& pal,
                const escritorio::themes::UIDensityMetrics& metrics,
                HFONT hFontTitle, HFONT hFontSmall, HFONT hFontMicro, HFONT hFontBody);

private:
    void RenderHeaderTabs(HDC hdc, const RECT& headerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontMicro);
    void RenderFooter(HDC hdc, const RECT& footerRect, const escritorio::themes::ThemePalette& pal, HFONT hFontSmall, HFONT hFontMicro);
    void RenderTabNotesSynopsis(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderTabBookmarks(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderTabMetadata(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderTabKeywords(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderTabSnapshots(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);
    void RenderTabComments(HDC hdc, const RECT& tabArea, const escritorio::themes::ThemePalette& pal, HFONT hFontTitle, HFONT hFontSmall, HFONT hFontBody);

    NativeInspectorTab m_activeTab = NativeInspectorTab::NotesSynopsis;

    // Documento
    std::wstring m_docUuid = L"doc-scene-1";
    std::wstring m_docTitle = L"Escena 1.1: La Niebla";

    // Pestaña 1
    bool m_synopsisImageMode = false;
    std::wstring m_synopsisText;
    std::wstring m_synopsisImagePath;
    std::wstring m_notesRtf;

    // Pie fijo
    int m_labelId = 1;
    std::wstring m_labelName = L"Capítulo 1";
    COLORREF m_labelColor = RGB(59, 130, 246);
    int m_statusId = 1;
    std::wstring m_statusName = L"Primer Borrador";

    // Pestaña 2
    bool m_bookmarkProjectScope = false;
    std::vector<NativeBookmarkItem> m_bookmarks;
    int m_selectedBookmarkIdx = 0;
    std::wstring m_bookmarkPreviewText;

    // Pestaña 3
    bool m_includeInCompile = true;
    std::wstring m_sectionType = L"Escena de Capítulo";
    std::vector<NativeCustomField> m_customFields;

    // Pestaña 4
    bool m_isKeywordsHudOpen = false;
    std::vector<std::pair<std::wstring, COLORREF>> m_keywords;

    // Pestaña 5
    std::vector<NativeSnapshotItem> m_snapshots;
    int m_selectedSnapshotIdx = 0;
    std::vector<NativeDiffSpan> m_diffSpans;

    // Pestaña 6
    std::vector<NativeCommentItem> m_comments;
    int m_selectedCommentIdx = -1;
};

} // namespace escritorio::ui
