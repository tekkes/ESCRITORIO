#include "ScriveningsEngine.hpp"
#include <sstream>
#include <algorithm>

namespace escritorio::ui {

size_t ScriveningsSectionNative::GetWordCount() const {
    size_t count = 0;
    bool inWord = false;
    for (wchar_t c : content) {
        if (iswspace(c) || iswpunct(c)) {
            inWord = false;
        } else if (!inWord) {
            inWord = true;
            count++;
        }
    }
    return count;
}

size_t ScriveningsSectionNative::GetCharCount() const {
    return content.length();
}

ScriveningsEngine::ScriveningsEngine() = default;

void ScriveningsEngine::Activate() {
    m_isActive = true;
}

void ScriveningsEngine::Deactivate() {
    m_isActive = false;
}

void ScriveningsEngine::Clear() {
    m_sections.clear();
    m_compositeText.clear();
    m_isActive = false;
}

void ScriveningsEngine::AddSection(const std::wstring& uuid, const std::wstring& title, const std::wstring& content) {
    ScriveningsSectionNative sec;
    sec.uuid = uuid;
    sec.title = title;
    sec.content = content;
    sec.isDirty = false;
    m_sections.push_back(sec);
    RebuildCompositeText();
    m_isActive = !m_sections.empty();
}

void ScriveningsEngine::SetDividerStyle(ScriveningsDividerStyle style) {
    m_dividerStyle = style;
    RebuildCompositeText();
}

void ScriveningsEngine::SetShowTitles(bool show, bool showNumbers) {
    m_showTitles = show;
    m_showNumbers = showNumbers;
    RebuildCompositeText();
}

std::wstring ScriveningsEngine::GetDividerString() const {
    switch (m_dividerStyle) {
    case ScriveningsDividerStyle::SubtleLine:
        return L"\r\n────────────────────────────────────────────────────────────\r\n";
    case ScriveningsDividerStyle::CornerCuts:
        return L"\r\n─── ✂ ─── ─── ✂ ─── ─── ✂ ─── ─── ✂ ─── ─── ✂ ───\r\n";
    case ScriveningsDividerStyle::PageBreak:
        return L"\r\n\x0C\r\n";
    }
    return L"\r\n────────────────────────────────────────────────────────────\r\n";
}

std::wstring ScriveningsEngine::FormatSectionHeader(const std::wstring& title, size_t sectionNum) const {
    std::wstringstream ss;
    if (m_showNumbers) {
        ss << L"\r\n### [" << sectionNum << L"] " << title << L" ###\r\n\r\n";
    } else {
        ss << L"\r\n### " << title << L" ###\r\n\r\n";
    }
    return ss.str();
}

void ScriveningsEngine::RebuildCompositeText() {
    std::wstringstream ss;
    size_t currentOffset = 0;
    std::wstring divider = GetDividerString();

    for (size_t i = 0; i < m_sections.size(); ++i) {
        auto& sec = m_sections[i];

        // 1. Encabezado
        if (m_showTitles) {
            std::wstring header = FormatSectionHeader(sec.title, i + 1);
            sec.headerStart = currentOffset;
            sec.headerEnd = currentOffset + header.length();
            currentOffset += header.length();
            ss << header;
        } else {
            sec.headerStart = currentOffset;
            sec.headerEnd = currentOffset;
        }

        // 2. Contenido
        sec.contentStart = currentOffset;
        sec.contentEnd = currentOffset + sec.content.length();
        currentOffset += sec.content.length();
        ss << sec.content;

        // 3. Separador (si no es la última)
        if (i + 1 < m_sections.size()) {
            sec.dividerStart = currentOffset;
            sec.dividerEnd = currentOffset + divider.length();
            currentOffset += divider.length();
            ss << divider;
        } else {
            sec.dividerStart = currentOffset;
            sec.dividerEnd = currentOffset;
        }
    }

    m_compositeText = ss.str();
}

ScriveningsSectionNative* ScriveningsEngine::GetSectionAtOffset(size_t offset) {
    for (auto& sec : m_sections) {
        if (offset >= sec.headerStart && offset <= sec.dividerEnd) {
            return &sec;
        }
    }
    return m_sections.empty() ? nullptr : &m_sections.back();
}

ScriveningsSectionNative* ScriveningsEngine::GetSectionByUuid(const std::wstring& uuid) {
    for (auto& sec : m_sections) {
        if (sec.uuid == uuid) {
            return &sec;
        }
    }
    return nullptr;
}

bool ScriveningsEngine::EditSectionTitle(const std::wstring& uuid, const std::wstring& newTitle) {
    auto* sec = GetSectionByUuid(uuid);
    if (!sec) return false;

    sec->title = newTitle;
    RebuildCompositeText();

    if (onTitleChanged) {
        onTitleChanged(uuid, newTitle);
    }
    return true;
}

bool ScriveningsEngine::EditSectionContent(const std::wstring& uuid, const std::wstring& newContent) {
    auto* sec = GetSectionByUuid(uuid);
    if (!sec) return false;

    sec->content = newContent;
    sec->isDirty = true;
    RebuildCompositeText();

    if (onContentSaved) {
        onContentSaved(uuid);
    }
    return true;
}

void ScriveningsEngine::UpdateFromCompositeEdit(size_t startOffset, size_t endOffset, const std::wstring& replacement) {
    auto* sec = GetSectionAtOffset(startOffset);
    if (!sec) return;

    if (startOffset >= sec->contentStart && startOffset <= sec->contentEnd) {
        size_t localStart = startOffset - sec->contentStart;
        size_t localEnd = (std::min)(endOffset, sec->contentEnd) - sec->contentStart;

        std::wstring newContent = sec->content.substr(0, localStart) + replacement;
        if (localEnd < sec->content.length()) {
            newContent += sec->content.substr(localEnd);
        }
        EditSectionContent(sec->uuid, newContent);
    }
}

size_t ScriveningsEngine::GetTotalWords() const {
    size_t total = 0;
    for (const auto& sec : m_sections) {
        total += sec.GetWordCount();
    }
    return total;
}

size_t ScriveningsEngine::GetTotalCharacters() const {
    size_t total = 0;
    for (const auto& sec : m_sections) {
        total += sec.GetCharCount();
    }
    return total;
}

} // namespace escritorio::ui
