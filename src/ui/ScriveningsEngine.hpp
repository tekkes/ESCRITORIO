#pragma once

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <string>
#include <vector>
#include <memory>
#include <functional>

namespace escritorio::ui {

enum class ScriveningsDividerStyle {
    SubtleLine,
    CornerCuts,
    PageBreak
};

struct ScriveningsSectionNative {
    std::wstring uuid;
    std::wstring title;
    std::wstring content;
    size_t headerStart = 0;
    size_t headerEnd = 0;
    size_t contentStart = 0;
    size_t contentEnd = 0;
    size_t dividerStart = 0;
    size_t dividerEnd = 0;
    bool isDirty = false;

    size_t GetWordCount() const;
    size_t GetCharCount() const;
};

class ScriveningsEngine {
public:
    ScriveningsEngine();
    ~ScriveningsEngine() = default;

    void Activate();
    void Deactivate();
    bool IsActive() const { return m_isActive; }

    void Clear();
    void AddSection(const std::wstring& uuid, const std::wstring& title, const std::wstring& content);

    void SetDividerStyle(ScriveningsDividerStyle style);
    ScriveningsDividerStyle GetDividerStyle() const { return m_dividerStyle; }

    void SetShowTitles(bool show, bool showNumbers = true);
    bool AreTitlesShown() const { return m_showTitles; }

    void RebuildCompositeText();
    const std::wstring& GetCompositeText() const { return m_compositeText; }

    bool EditSectionTitle(const std::wstring& uuid, const std::wstring& newTitle);
    bool EditSectionContent(const std::wstring& uuid, const std::wstring& newContent);
    void UpdateFromCompositeEdit(size_t startOffset, size_t endOffset, const std::wstring& replacement);

    size_t GetTotalWords() const;
    size_t GetTotalCharacters() const;
    size_t GetSectionCount() const { return m_sections.size(); }
    const std::vector<ScriveningsSectionNative>& GetSections() const { return m_sections; }
    ScriveningsSectionNative* GetSectionAtOffset(size_t offset);
    ScriveningsSectionNative* GetSectionByUuid(const std::wstring& uuid);

    // Callbacks
    std::function<void(const std::wstring& uuid, const std::wstring& newTitle)> onTitleChanged;
    std::function<void(const std::wstring& uuid)> onContentSaved;

private:
    bool m_isActive = false;
    ScriveningsDividerStyle m_dividerStyle = ScriveningsDividerStyle::SubtleLine;
    bool m_showTitles = true;
    bool m_showNumbers = true;
    std::wstring m_compositeText;
    std::vector<ScriveningsSectionNative> m_sections;

    std::wstring GetDividerString() const;
    std::wstring FormatSectionHeader(const std::wstring& title, size_t sectionNum) const;
};

} // namespace escritorio::ui
