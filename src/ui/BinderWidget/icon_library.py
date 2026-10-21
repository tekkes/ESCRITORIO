"""
Biblioteca de Micro-Iconos Vectoriales SVG para el Binder de Escritorio
Más de 80 micro-iconos optimizados para alta densidad visual (14px / 16px),
categorizados en Carpetas, Documentos, Personajes, Lugares, Objetos, Alertas,
Banderas cromáticas y Generador dinámico de Iconos por Emoji/Texto.
"""

from typing import Dict, List, Optional

class IconLibrary:
    """Catálogo y generador de iconos vectoriales SVG para el Cuaderno (Binder)."""

    # Diccionario maestro de más de 80 micro-iconos SVG
    ICONS: Dict[str, str] = {
        # --- CARPETAS DEL SISTEMA Y COMUNES (20) ---
        "folder_draft": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" fill="#3B82F6" fill-opacity="0.2" stroke="#3B82F6" stroke-width="1.2"/><path d="M6 7.5L10 11.5M10 7.5L6 11.5" stroke="#3B82F6" stroke-width="1.1"/></svg>',
        "folder_research": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" fill="#10B981" fill-opacity="0.2" stroke="#10B981" stroke-width="1.2"/><circle cx="8" cy="9" r="2.5" stroke="#10B981" stroke-width="1.1"/><path d="M10 11L12 13" stroke="#10B981" stroke-width="1.2" stroke-linecap="round"/></svg>',
        "folder_trash": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" fill="#EF4444" fill-opacity="0.2" stroke="#EF4444" stroke-width="1.2"/><path d="M5.5 7.5L6 12M10.5 7.5L10 12M8 7.5V12" stroke="#EF4444" stroke-width="1.1"/></svg>',
        "folder_templates": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" fill="#8B5CF6" fill-opacity="0.2" stroke="#8B5CF6" stroke-width="1.2"/><rect x="6" y="7" width="4" height="4" rx="0.5" stroke="#8B5CF6" stroke-width="1.1"/></svg>',
        "folder_standard": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" fill="#F59E0B" fill-opacity="0.2" stroke="#F59E0B" stroke-width="1.2"/></svg>',
        "folder_open": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#F59E0B" stroke-width="1.2"/><path d="M1 14L3 7H15L13 14H1Z" fill="#FBBF24" fill-opacity="0.3" stroke="#F59E0B" stroke-width="1.1"/></svg>',
        "folder_locked": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#64748B" stroke-width="1.2"/><rect x="6.5" y="8" width="4" height="3" rx="0.5" fill="#64748B"/><path d="M7.5 8V6.5C7.5 5.95 7.95 5.5 8.5 5.5C9.05 5.5 9.5 5.95 9.5 6.5V8" stroke="#64748B" stroke-width="1"/></svg>',
        "folder_star": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#EAB308" stroke-width="1.2"/><polygon points="8,6 9,8.5 11.5,8.5 9.5,10 10.5,12 8,10.8 5.5,12 6.5,10 4.5,8.5 7,8.5" fill="#EAB308"/></svg>',
        "folder_heart": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#EC4899" stroke-width="1.2"/><path d="M8 11.5L6 9.5C5 8.5 5 7 6 6C7 5 8.5 6 8.5 6C8.5 6 10 5 11 6C12 7 12 8.5 11 9.5L8 11.5Z" fill="#EC4899"/></svg>',
        "folder_bookmark": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#06B6D4" stroke-width="1.2"/><path d="M8 6V11L9.5 9.8L11 11V6H8Z" fill="#06B6D4"/></svg>',
        "folder_archive": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#78716C" stroke-width="1.2"/><line x1="6" y1="8" x2="10" y2="8" stroke="#78716C" stroke-width="1.2"/></svg>',
        "folder_characters": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#A855F7" stroke-width="1.2"/><circle cx="8" cy="7.5" r="1.5" fill="#A855F7"/><path d="M6 11.5C6 10 7 9.5 8 9.5C9 9.5 10 10 10 11.5" stroke="#A855F7" stroke-width="1.1"/></svg>',
        "folder_places": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#14B8A6" stroke-width="1.2"/><path d="M8 6C7 6 6 7 6 8C6 9.5 8 11.5 8 11.5C8 11.5 10 9.5 10 8C10 7 9 6 8 6Z" fill="#14B8A6"/></svg>',
        "folder_ideas": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#FBBF24" stroke-width="1.2"/><circle cx="8" cy="8" r="1.8" fill="#FBBF24"/><line x1="8" y1="10.5" x2="8" y2="11.5" stroke="#FBBF24" stroke-width="1.2"/></svg>',
        "folder_notes": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#84CC16" stroke-width="1.2"/><line x1="5.5" y1="7.5" x2="10.5" y2="7.5" stroke="#84CC16" stroke-width="1"/><line x1="5.5" y1="9.5" x2="9.5" y2="9.5" stroke="#84CC16" stroke-width="1"/></svg>',
        "folder_audio": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#6366F1" stroke-width="1.2"/><path d="M7 10V7L10 6V9" stroke="#6366F1" stroke-width="1.1"/></svg>',
        "folder_video": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#D946EF" stroke-width="1.2"/><polygon points="7,7 10,8.5 7,10" fill="#D946EF"/></svg>',
        "folder_code": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#059669" stroke-width="1.2"/><path d="M6 7L4.5 8.5L6 10M10 7L11.5 8.5L10 10" stroke="#059669" stroke-width="1.1"/></svg>',
        "folder_web": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 3.5C2 2.67 2.67 2 3.5 2H6.5L8 4H12.5C13.33 4 14 4.67 14 5.5V12.5C14 13.33 13.33 14 12.5 14H3.5C2.67 14 2 13.33 2 12.5V3.5Z" stroke="#0284C7" stroke-width="1.2"/><circle cx="8" cy="8.5" r="2.5" stroke="#0284C7" stroke-width="1"/></svg>',
        "folder_sub": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 4.5C3 3.67 3.67 3 4.5 3H7L8.5 5H12C12.83 5 13.5 5.67 13.5 6.5V11.5C13.5 12.33 12.83 13 12 13H4.5C3.67 13 3 12.33 3 11.5V4.5Z" stroke="#94A3B8" stroke-width="1.2"/></svg>',

        # --- DOCUMENTOS DE TEXTO Y NARRATIVA (15) ---
        "doc_text": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" fill="#F8FAFC" stroke="#64748B" stroke-width="1.2"/><path d="M9.5 2V5H12.5" stroke="#64748B" stroke-width="1.2"/><line x1="5" y1="7.5" x2="10" y2="7.5" stroke="#94A3B8" stroke-width="1"/><line x1="5" y1="9.5" x2="10" y2="9.5" stroke="#94A3B8" stroke-width="1"/><line x1="5" y1="11.5" x2="8" y2="11.5" stroke="#94A3B8" stroke-width="1"/></svg>',
        "doc_chapter": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" fill="#EFF6FF" stroke="#3B82F6" stroke-width="1.2"/><path d="M9.5 2V5H12.5" stroke="#3B82F6" stroke-width="1.2"/><rect x="5" y="7" width="5" height="2" rx="0.5" fill="#3B82F6"/></svg>',
        "doc_scene": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" fill="#F0FDF4" stroke="#10B981" stroke-width="1.2"/><path d="M9.5 2V5H12.5" stroke="#10B981" stroke-width="1.2"/><circle cx="7.5" cy="9" r="1.8" fill="#10B981"/></svg>',
        "doc_synopsis": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" fill="#FEFCE8" stroke="#EAB308" stroke-width="1.2"/><rect x="5" y="7" width="6" height="4" rx="0.5" stroke="#EAB308" stroke-width="1"/></svg>',
        "doc_notes": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" fill="#FAF5FF" stroke="#A855F7" stroke-width="1.2"/><path d="M5.5 8L8.5 11L11 6" stroke="#A855F7" stroke-width="1.2"/></svg>',
        "doc_script": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#F97316" stroke-width="1.2"/><path d="M5 8H10M7.5 8V12" stroke="#F97316" stroke-width="1.2"/></svg>',
        "doc_code": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#059669" stroke-width="1.2"/><path d="M6 8L5 9L6 10M9 8L10 9L9 10" stroke="#059669" stroke-width="1.1"/></svg>',
        "doc_poem": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#EC4899" stroke-width="1.2"/><path d="M6 7.5Q7.5 6.5 8 8Q8.5 9.5 10 8.5" stroke="#EC4899" stroke-width="1.2"/></svg>',
        "doc_character": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#8B5CF6" stroke-width="1.2"/><circle cx="7.5" cy="7.5" r="1.3" fill="#8B5CF6"/><path d="M6 11C6 10 6.8 9.5 7.5 9.5C8.2 9.5 9 10 9 11" stroke="#8B5CF6" stroke-width="1"/></svg>',
        "doc_setting": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#14B8A6" stroke-width="1.2"/><polygon points="7.5,7 9.5,11 5.5,11" stroke="#14B8A6" stroke-width="1"/></svg>',
        "doc_checklist": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#64748B" stroke-width="1.2"/><rect x="5" y="7" width="2" height="2" fill="#10B981"/><rect x="5" y="10" width="2" height="2" fill="#64748B"/></svg>',
        "doc_timeline": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#F59E0B" stroke-width="1.2"/><line x1="5.5" y1="8" x2="10" y2="8" stroke="#F59E0B" stroke-width="1.5"/><circle cx="7" cy="8" r="1.5" fill="#EF4444"/></svg>',
        "doc_worldbuilding": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#6366F1" stroke-width="1.2"/><circle cx="7.5" cy="8.5" r="2.3" stroke="#6366F1" stroke-width="1"/></svg>',
        "doc_sheet": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#475569" stroke-width="1.2"/><rect x="5" y="7" width="5" height="4" stroke="#475569" stroke-width="0.8"/></svg>',
        "doc_memo": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2H9.5L12.5 5V13.5C12.5 13.78 12.28 14 12 14H3.5C3.22 14 3 13.78 3 13.5V2.5C3 2.22 3.22 2 3.5 2Z" stroke="#D97706" stroke-width="1.2"/><line x1="5" y1="8" x2="9" y2="8" stroke="#D97706" stroke-width="1.2"/></svg>',

        # --- PERSONAJES (12) ---
        "char_protagonist": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="#3B82F6" stroke-width="1.2"/><path d="M3.5 13.5C3.5 11 5.5 9 8 9C10.5 9 12.5 11 12.5 13.5" stroke="#3B82F6" stroke-width="1.2"/><polygon points="8,1 8.8,2.8 10.5,2.8 9.2,3.8 9.8,5.5 8,4.5 6.2,5.5 6.8,3.8 5.5,2.8 7.2,2.8" fill="#FBBF24"/></svg>',
        "char_antagonist": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="#EF4444" stroke-width="1.2"/><path d="M3.5 13.5C3.5 11 5.5 9 8 9C10.5 9 12.5 11 12.5 13.5" stroke="#EF4444" stroke-width="1.2"/><path d="M6 3.5L8 5L10 3.5" stroke="#EF4444" stroke-width="1.2"/></svg>',
        "char_supporting": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="#10B981" stroke-width="1.2"/><path d="M4 13.5C4 11.2 5.8 9.5 8 9.5C10.2 9.5 12 11.2 12 13.5" stroke="#10B981" stroke-width="1.2"/></svg>',
        "char_mask": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2.5 6C2.5 4 4.5 3 8 3C11.5 3 13.5 4 13.5 6C13.5 10 10 13 8 13C6 13 2.5 10 2.5 6Z" stroke="#8B5CF6" stroke-width="1.2"/><circle cx="5.5" cy="6.5" r="1" fill="#8B5CF6"/><circle cx="10.5" cy="6.5" r="1" fill="#8B5CF6"/></svg>',
        "char_detective": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><ellipse cx="8" cy="8" rx="4" ry="3" stroke="#64748B" stroke-width="1.2"/><path d="M4 8L8 4L12 8" stroke="#64748B" stroke-width="1.2"/><line x1="2" y1="8" x2="14" y2="8" stroke="#64748B" stroke-width="1.2"/></svg>',
        "char_crown": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2.5 12.5H13.5L12.5 5L9.5 8L8 4L6.5 8L3.5 5L2.5 12.5Z" fill="#F59E0B" stroke="#D97706" stroke-width="1.2"/></svg>',
        "char_mentor": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="2.5" stroke="#F59E0B" stroke-width="1.2"/><path d="M6 7.5L8 10L10 7.5" stroke="#F59E0B" stroke-width="1.2"/><path d="M4 13.5C4 11.5 5.8 10 8 10C10.2 10 12 11.5 12 13.5" stroke="#F59E0B" stroke-width="1.2"/></svg>',
        "char_group": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="2" stroke="#6366F1" stroke-width="1"/><circle cx="10" cy="5" r="2" stroke="#6366F1" stroke-width="1"/><path d="M2.5 13C2.5 11 4 10 6 10C8 10 9.5 11 9.5 13" stroke="#6366F1" stroke-width="1"/><path d="M10.5 10C12 10 13.5 11 13.5 13" stroke="#6366F1" stroke-width="1"/></svg>',
        "char_robot": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="4" y="5" width="8" height="7" rx="1.5" stroke="#06B6D4" stroke-width="1.2"/><circle cx="6.5" cy="8" r="0.8" fill="#06B6D4"/><circle cx="9.5" cy="8" r="0.8" fill="#06B6D4"/><line x1="8" y1="2" x2="8" y2="5" stroke="#06B6D4" stroke-width="1.2"/></svg>',
        "char_skull": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="7" r="4.5" stroke="#64748B" stroke-width="1.2"/><circle cx="6.5" cy="7" r="1" fill="#64748B"/><circle cx="9.5" cy="7" r="1" fill="#64748B"/><rect x="6.5" y="10.5" width="3" height="2" stroke="#64748B" stroke-width="1"/></svg>',
        "char_female": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="6" r="3" stroke="#EC4899" stroke-width="1.2"/><line x1="8" y1="9" x2="8" y2="14" stroke="#EC4899" stroke-width="1.2"/><line x1="6" y1="11.5" x2="10" y2="11.5" stroke="#EC4899" stroke-width="1.2"/></svg>',
        "char_male": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6.5" cy="9.5" r="3" stroke="#3B82F6" stroke-width="1.2"/><line x1="9" y1="7" x2="13.5" y2="2.5" stroke="#3B82F6" stroke-width="1.2"/><polyline points="10,2.5 13.5,2.5 13.5,6" stroke="#3B82F6" stroke-width="1.2"/></svg>',

        # --- ESCENARIOS Y LUGARES (10) ---
        "loc_castle": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="3" y="6" width="10" height="7" stroke="#64748B" stroke-width="1.2"/><path d="M3 6V4H5V5H7V4H9V5H11V4H13V6" stroke="#64748B" stroke-width="1.2"/><rect x="6.5" y="10" width="3" height="3" fill="#64748B"/></svg>',
        "loc_city": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="3" y="6" width="4" height="7" stroke="#475569" stroke-width="1.2"/><rect x="7" y="3" width="5" height="10" stroke="#475569" stroke-width="1.2"/><line x1="8.5" y1="5" x2="10.5" y2="5" stroke="#475569" stroke-width="1"/><line x1="8.5" y1="7" x2="10.5" y2="7" stroke="#475569" stroke-width="1"/></svg>',
        "loc_house": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><polygon points="8,2.5 2.5,7 4,7 4,13.5 12,13.5 12,7 13.5,7" stroke="#D97706" stroke-width="1.2"/><rect x="6.5" y="9.5" width="3" height="4" stroke="#D97706" stroke-width="1"/></svg>',
        "loc_mountain": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><polygon points="2,13 7.5,4 10.5,9 14,13" stroke="#65A30D" stroke-width="1.2"/><polygon points="6,6.5 7.5,4 9,6.5" fill="#65A30D"/></svg>',
        "loc_forest": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><polygon points="8,2.5 5,7 6.5,7 4,11 12,11 9.5,7 11,7" fill="#15803D" stroke="#15803D" stroke-width="1.1"/><line x1="8" y1="11" x2="8" y2="13.5" stroke="#78350F" stroke-width="1.5"/></svg>',
        "loc_space": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M12.5 3.5C12.5 3.5 9 4 7 6C5 8 4.5 11.5 4.5 11.5L6 13C6 13 9.5 12.5 11.5 10.5C13.5 8.5 14 5 14 5L12.5 3.5Z" stroke="#8B5CF6" stroke-width="1.2"/><circle cx="9.5" cy="6.5" r="1" fill="#8B5CF6"/></svg>',
        "loc_sea": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 9Q4 7.5 6 9Q8 10.5 10 9Q12 7.5 14 9" stroke="#0284C7" stroke-width="1.2"/><path d="M2 12Q4 10.5 6 12Q8 13.5 10 12Q12 10.5 14 12" stroke="#0284C7" stroke-width="1.2"/></svg>',
        "loc_compass": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#EA580C" stroke-width="1.2"/><polygon points="8,4.5 9.5,8 8,11.5 6.5,8" fill="#EA580C"/></svg>',
        "loc_map": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><polygon points="3,4 6.5,2.5 9.5,4 13,2.5 13,12 9.5,13.5 6.5,12 3,13.5" stroke="#D97706" stroke-width="1.2"/><line x1="6.5" y1="2.5" x2="6.5" y2="12" stroke="#D97706" stroke-width="1.1"/><line x1="9.5" y1="4" x2="9.5" y2="13.5" stroke="#D97706" stroke-width="1.1"/></svg>',
        "loc_ruins": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="3" y="5" width="2" height="8" stroke="#78716C" stroke-width="1.2"/><rect x="7" y="7" width="2" height="6" stroke="#78716C" stroke-width="1.2"/><rect x="11" y="9" width="2" height="4" stroke="#78716C" stroke-width="1.2"/><line x1="2" y1="13" x2="14" y2="13" stroke="#78716C" stroke-width="1.2"/></svg>',

        # --- OBJETOS Y CREATIVIDAD (10) ---
        "obj_quill": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M13.5 2.5C13.5 2.5 10 3 7 7C4 11 3 13.5 3 13.5L5.5 13L13.5 2.5Z" stroke="#4F46E5" stroke-width="1.2"/><line x1="8" y1="6" x2="10" y2="8" stroke="#4F46E5" stroke-width="1"/></svg>',
        "obj_book": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2.5 4C2.5 4 5 3 8 4.5C11 3 13.5 4 13.5 4V12.5C13.5 12.5 11 11.5 8 13C5 11.5 2.5 12.5 2.5 12.5V4Z" stroke="#B45309" stroke-width="1.2"/><line x1="8" y1="4.5" x2="8" y2="13" stroke="#B45309" stroke-width="1.2"/></svg>',
        "obj_scroll": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 3.5H12C12.8 3.5 13.5 4.2 13.5 5V12C13.5 12.8 12.8 13.5 12 13.5H4C3.2 13.5 2.5 12.8 2.5 12V4C2.5 3.2 3.2 2.5 4 2.5C4.8 2.5 5.5 3.2 5.5 4V12" stroke="#CA8A04" stroke-width="1.2"/></svg>',
        "obj_key": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="5.5" cy="6.5" r="2.5" stroke="#EAB308" stroke-width="1.2"/><line x1="7.5" y1="8.5" x2="13" y2="14" stroke="#EAB308" stroke-width="1.2"/><line x1="11" y1="12" x2="12" y2="11" stroke="#EAB308" stroke-width="1.2"/><line x1="12.5" y1="13.5" x2="13.5" y2="12.5" stroke="#EAB308" stroke-width="1.2"/></svg>',
        "obj_dagger": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><line x1="3" y1="13" x2="10" y2="6" stroke="#94A3B8" stroke-width="1.5"/><line x1="8" y1="4" x2="12" y2="8" stroke="#EAB308" stroke-width="1.2"/><line x1="10" y1="6" x2="14" y2="2" stroke="#94A3B8" stroke-width="1.2"/></svg>',
        "obj_potion": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M6.5 2.5H9.5V5L12.5 11C13 12 12.5 13.5 11 13.5H5C3.5 13.5 3 12 3.5 11L6.5 5V2.5Z" stroke="#9333EA" stroke-width="1.2"/><line x1="4.5" y1="10" x2="11.5" y2="10" stroke="#9333EA" stroke-width="1"/></svg>',
        "obj_lightbulb": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M5.5 6C5.5 4.5 6.5 3 8 3C9.5 3 10.5 4.5 10.5 6C10.5 7.5 9.5 8.5 9.5 10H6.5C6.5 8.5 5.5 7.5 5.5 6Z" fill="#FBBF24" stroke="#F59E0B" stroke-width="1.2"/><line x1="6.5" y1="12" x2="9.5" y2="12" stroke="#F59E0B" stroke-width="1.2"/></svg>',
        "obj_clock": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#3B82F6" stroke-width="1.2"/><polyline points="8,5 8,8 10.5,8" stroke="#3B82F6" stroke-width="1.2"/></svg>',
        "obj_camera": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2.5" y="5" width="11" height="8" rx="1.5" stroke="#475569" stroke-width="1.2"/><polygon points="5,5 6,3 10,3 11,5" stroke="#475569" stroke-width="1"/><circle cx="8" cy="9" r="2" stroke="#475569" stroke-width="1.2"/></svg>',
        "obj_brush": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M12.5 3.5L10 6L7 3L9.5 0.5L12.5 3.5Z" fill="#F43F5E"/><path d="M7 6L3 10C2.5 11 2 13 2 13C2 13 4 12.5 5 12L9 8" stroke="#F43F5E" stroke-width="1.2"/></svg>',

        # --- BANDERAS CROMÁTICAS (10) ---
        "flag_red": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#EF4444" stroke-width="1.2" fill="#EF4444"/></svg>',
        "flag_blue": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#3B82F6" stroke-width="1.2" fill="#3B82F6"/></svg>',
        "flag_green": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#10B981" stroke-width="1.2" fill="#10B981"/></svg>',
        "flag_yellow": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#EAB308" stroke-width="1.2" fill="#EAB308"/></svg>',
        "flag_purple": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#A855F7" stroke-width="1.2" fill="#A855F7"/></svg>',
        "flag_orange": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#F97316" stroke-width="1.2" fill="#F97316"/></svg>',
        "flag_cyan": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#06B6D4" stroke-width="1.2" fill="#06B6D4"/></svg>',
        "flag_pink": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#EC4899" stroke-width="1.2" fill="#EC4899"/></svg>',
        "flag_black": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#1E293B" stroke-width="1.2" fill="#1E293B"/></svg>',
        "flag_white": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 2V14M3.5 2.5H12L9.5 6L12 9.5H3.5" stroke="#94A3B8" stroke-width="1.2" fill="#F8FAFC"/></svg>',

        # --- ESTADOS Y ALERTAS (10) ---
        "alert_warning": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><polygon points="8,2.5 14,13.5 2,13.5" fill="#F59E0B" stroke="#D97706" stroke-width="1.1"/><line x1="8" y1="6.5" x2="8" y2="9.5" stroke="#FFFFFF" stroke-width="1.2"/><circle cx="8" cy="11.5" r="0.7" fill="#FFFFFF"/></svg>',
        "alert_danger": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" fill="#EF4444" stroke="#DC2626" stroke-width="1.1"/><line x1="8" y1="5" x2="8" y2="8.5" stroke="#FFFFFF" stroke-width="1.2"/><circle cx="8" cy="11" r="0.7" fill="#FFFFFF"/></svg>',
        "alert_info": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" fill="#3B82F6" stroke="#2563EB" stroke-width="1.1"/><circle cx="8" cy="5.5" r="0.7" fill="#FFFFFF"/><line x1="8" y1="7.5" x2="8" y2="11" stroke="#FFFFFF" stroke-width="1.2"/></svg>',
        "status_check": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" fill="#10B981" stroke="#059669" stroke-width="1.1"/><path d="M5.5 8L7 9.5L10.5 6" stroke="#FFFFFF" stroke-width="1.2" stroke-linecap="round"/></svg>',
        "status_target": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#EF4444" stroke-width="1.2"/><circle cx="8" cy="8" r="3" stroke="#EF4444" stroke-width="1"/><circle cx="8" cy="8" r="1" fill="#EF4444"/></svg>',
        "status_hourglass": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 3H12M4 13H12M5 3C5 6 7 7 8 8C9 7 11 6 11 3M5 13C5 10 7 9 8 8C9 9 11 10 11 13" stroke="#F59E0B" stroke-width="1.2"/></svg>',
        "status_flame": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2.5C8 2.5 10.5 5 10.5 8C10.5 10.5 9 12.5 8 13.5C7 12.5 5.5 10.5 5.5 8C5.5 6 6.5 4.5 8 2.5Z" fill="#F97316" stroke="#EA580C" stroke-width="1.1"/></svg>',
        "status_shield": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2.5L12.5 4.5V8C12.5 11 10 13 8 13.5C6 13 3.5 11 3.5 8V4.5L8 2.5Z" stroke="#6366F1" stroke-width="1.2"/></svg>',
        "status_cross": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#EF4444" stroke-width="1.2"/><line x1="6" y1="6" x2="10" y2="10" stroke="#EF4444" stroke-width="1.2"/><line x1="10" y1="6" x2="6" y2="10" stroke="#EF4444" stroke-width="1.2"/></svg>',
        "status_question": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="5.5" stroke="#8B5CF6" stroke-width="1.2"/><path d="M6.5 6.5C6.5 5.5 7.2 4.8 8 4.8C8.8 4.8 9.5 5.5 9.5 6.5C9.5 7.5 8 8 8 9" stroke="#8B5CF6" stroke-width="1.2"/><circle cx="8" cy="11" r="0.6" fill="#8B5CF6"/></svg>'
    }

    @classmethod
    def get_icon(cls, icon_id: str, fallback: str = "doc_text") -> str:
        """Devuelve el marcado SVG de un icono por su identificador."""
        return cls.ICONS.get(icon_id, cls.ICONS.get(fallback, ""))

    @classmethod
    def get_categories(cls) -> Dict[str, List[Dict[str, str]]]:
        """Organiza la biblioteca de más de 80 iconos en categorías para el menú contextual."""
        categories = {
            "Carpetas": [
                {"id": "folder_standard", "name": "Carpeta Estándar"},
                {"id": "folder_draft", "name": "Borrador"},
                {"id": "folder_research", "name": "Investigación"},
                {"id": "folder_trash", "name": "Papelera"},
                {"id": "folder_templates", "name": "Plantillas"},
                {"id": "folder_open", "name": "Carpeta Abierta"},
                {"id": "folder_locked", "name": "Carpeta Bloqueada"},
                {"id": "folder_star", "name": "Favorito"},
                {"id": "folder_heart", "name": "Corazón"},
                {"id": "folder_bookmark", "name": "Marcador"},
                {"id": "folder_archive", "name": "Archivo"},
                {"id": "folder_characters", "name": "Personajes"},
                {"id": "folder_places", "name": "Lugares"},
                {"id": "folder_ideas", "name": "Ideas"},
                {"id": "folder_notes", "name": "Notas"},
                {"id": "folder_audio", "name": "Audio"},
                {"id": "folder_video", "name": "Vídeo"},
                {"id": "folder_code", "name": "Código"},
                {"id": "folder_web", "name": "Web"},
                {"id": "folder_sub", "name": "Subcarpeta"}
            ],
            "Documentos": [
                {"id": "doc_text", "name": "Documento de Texto"},
                {"id": "doc_chapter", "name": "Capítulo"},
                {"id": "doc_scene", "name": "Escena"},
                {"id": "doc_synopsis", "name": "Sinopsis"},
                {"id": "doc_notes", "name": "Notas"},
                {"id": "doc_script", "name": "Guión"},
                {"id": "doc_code", "name": "Código"},
                {"id": "doc_poem", "name": "Poesía"},
                {"id": "doc_character", "name": "Ficha Personaje"},
                {"id": "doc_setting", "name": "Ficha Lugar"},
                {"id": "doc_checklist", "name": "Lista Tareas"},
                {"id": "doc_timeline", "name": "Cronología"},
                {"id": "doc_worldbuilding", "name": "Construcción de Mundo"},
                {"id": "doc_sheet", "name": "Hoja de Cálculo"},
                {"id": "doc_memo", "name": "Memorándum"}
            ],
            "Personajes": [
                {"id": "char_protagonist", "name": "Protagonista"},
                {"id": "char_antagonist", "name": "Antagonista"},
                {"id": "char_supporting", "name": "Secundario"},
                {"id": "char_mentor", "name": "Mentor"},
                {"id": "char_detective", "name": "Investigador"},
                {"id": "char_crown", "name": "Realeza"},
                {"id": "char_mask", "name": "Misterio"},
                {"id": "char_group", "name": "Grupo / Facción"},
                {"id": "char_robot", "name": "Cíborg / IA"},
                {"id": "char_skull", "name": "Enemigo / Mortal"},
                {"id": "char_female", "name": "Femenino"},
                {"id": "char_male", "name": "Masculino"}
            ],
            "Lugares": [
                {"id": "loc_castle", "name": "Castillo / Fortaleza"},
                {"id": "loc_city", "name": "Ciudad"},
                {"id": "loc_house", "name": "Casa"},
                {"id": "loc_mountain", "name": "Montaña"},
                {"id": "loc_forest", "name": "Bosque"},
                {"id": "loc_space", "name": "Espacio Exterior"},
                {"id": "loc_sea", "name": "Mar / Océano"},
                {"id": "loc_compass", "name": "Brújula"},
                {"id": "loc_map", "name": "Mapa"},
                {"id": "loc_ruins", "name": "Ruinas"}
            ],
            "Objetos y Creatividad": [
                {"id": "obj_quill", "name": "Pluma"},
                {"id": "obj_book", "name": "Libro"},
                {"id": "obj_scroll", "name": "Pergamino"},
                {"id": "obj_key", "name": "Llave"},
                {"id": "obj_dagger", "name": "Daga"},
                {"id": "obj_potion", "name": "Poción"},
                {"id": "obj_lightbulb", "name": "Bombilla"},
                {"id": "obj_clock", "name": "Reloj"},
                {"id": "obj_camera", "name": "Cámara"},
                {"id": "obj_brush", "name": "Pincel"}
            ],
            "Banderas": [
                {"id": "flag_red", "name": "Bandera Roja"},
                {"id": "flag_blue", "name": "Bandera Azul"},
                {"id": "flag_green", "name": "Bandera Verde"},
                {"id": "flag_yellow", "name": "Bandera Amarilla"},
                {"id": "flag_purple", "name": "Bandera Púrpura"},
                {"id": "flag_orange", "name": "Bandera Naranja"},
                {"id": "flag_cyan", "name": "Bandera Cian"},
                {"id": "flag_pink", "name": "Bandera Rosa"},
                {"id": "flag_black", "name": "Bandera Negra"},
                {"id": "flag_white", "name": "Bandera Blanca"}
            ],
            "Estados": [
                {"id": "status_check", "name": "Completado"},
                {"id": "alert_warning", "name": "Revisión Pendiente"},
                {"id": "alert_danger", "name": "Alerta / Conflicto"},
                {"id": "alert_info", "name": "Información"},
                {"id": "status_target", "name": "Objetivo"},
                {"id": "status_hourglass", "name": "En Espera"},
                {"id": "status_flame", "name": "Urgente"},
                {"id": "status_shield", "name": "Protegido"},
                {"id": "status_cross", "name": "Descartado"},
                {"id": "status_question", "name": "Duda"}
            ]
        }
        return categories

    @classmethod
    def generate_emoji_svg(cls, emoji_or_text: str, bg_color: Optional[str] = None) -> str:
        """
        Genera un icono SVG dinámico a partir de 1-2 caracteres o un emoji unicode.
        """
        char = (emoji_or_text or "★")[:2]
        bg_rect = f'<rect width="16" height="16" rx="3" fill="{bg_color}"/>' if bg_color else ""
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">'
            f'{bg_rect}'
            f'<text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle" '
            f'font-size="11" font-family="Segoe UI Emoji, Apple Color Emoji, sans-serif">{char}</text>'
            f'</svg>'
        )

    @classmethod
    def count(cls) -> int:
        """Retorna el número total de iconos integrados (superior a 80)."""
        return len(cls.ICONS)
