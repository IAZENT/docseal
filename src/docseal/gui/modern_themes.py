"""Enhanced modern theme system for DocSeal GUI."""

from dataclasses import dataclass


@dataclass
class ModernTheme:
    """Modern theme configuration."""

    # Primary colors
    primary_bg: str
    primary_text: str
    secondary_bg: str
    secondary_text: str

    # UI element colors
    button_bg: str
    button_text: str
    button_hover: str
    button_pressed: str
    button_disabled: str

    # Input field colors
    input_bg: str
    input_text: str
    input_border: str
    input_focus_border: str

    # Status colors
    success_color: str
    error_color: str
    warning_color: str
    info_color: str

    # Sidebar
    sidebar_bg: str
    sidebar_text: str
    sidebar_hover: str
    sidebar_active: str

    # Other
    border_color: str
    shadow_color: str
    label_text: str
    accent_color: str

    def get_stylesheet(self) -> str:
        """Generate complete stylesheet."""
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {self.primary_bg};
            color: {self.primary_text};
        }}

        /* General Widget */
        QWidget {{
            background-color: {self.primary_bg};
            color: {self.primary_text};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {self.button_bg};
            color: {self.button_text};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 11pt;
        }}

        QPushButton:hover {{
            background-color: {self.button_hover};
        }}

        QPushButton:pressed {{
            background-color: {self.button_pressed};
        }}

        QPushButton:disabled {{
            background-color: {self.button_disabled};
            color: #999999;
        }}

        /* Input Fields */
        QLineEdit {{
            background-color: {self.input_bg};
            color: {self.input_text};
            border: 1px solid {self.input_border};
            border-radius: 4px;
            padding: 8px;
            selection-background-color: {self.accent_color};
        }}

        QLineEdit:focus {{
            border: 2px solid {self.input_focus_border};
        }}

        QTextEdit {{
            background-color: {self.input_bg};
            color: {self.input_text};
            border: 1px solid {self.input_border};
            border-radius: 4px;
            padding: 8px;
        }}

        QTextEdit:focus {{
            border: 2px solid {self.input_focus_border};
        }}

        /* Combo Box */
        QComboBox {{
            background-color: {self.input_bg};
            color: {self.input_text};
            border: 1px solid {self.input_border};
            border-radius: 4px;
            padding: 5px;
        }}

        QComboBox:hover {{
            border: 1px solid {self.input_focus_border};
        }}

        QComboBox QAbstractItemView {{
            background-color: {self.secondary_bg};
            color: {self.primary_text};
            selection-background-color: {self.accent_color};
        }}

        /* Labels */
        QLabel {{
            color: {self.label_text};
        }}

        /* Group Box */
        QGroupBox {{
            border: 1px solid {self.border_color};
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            color: {self.label_text};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }}

        /* Checkbox */
        QCheckBox {{
            color: {self.primary_text};
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 1px solid {self.input_border};
            background-color: {self.input_bg};
        }}

        QCheckBox::indicator:hover {{
            border: 1px solid {self.input_focus_border};
        }}

        QCheckBox::indicator:checked {{
            background-color: {self.accent_color};
            border: 1px solid {self.accent_color};
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {self.secondary_bg};
            color: {self.primary_text};
            border-bottom: 1px solid {self.border_color};
        }}

        QMenuBar::item:selected {{
            background-color: {self.button_hover};
        }}

        /* Menu */
        QMenu {{
            background-color: {self.secondary_bg};
            color: {self.primary_text};
            border: 1px solid {self.border_color};
        }}

        QMenu::item:selected {{
            background-color: {self.accent_color};
            color: {self.button_text};
        }}

        /* Scroll Bar */
        QScrollBar:vertical {{
            background-color: {self.primary_bg};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {self.border_color};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {self.accent_color};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {self.border_color};
        }}

        QTabBar::tab {{
            background-color: {self.secondary_bg};
            color: {self.primary_text};
            padding: 8px 20px;
            border: 1px solid {self.border_color};
        }}

        QTabBar::tab:selected {{
            background-color: {self.button_bg};
            border-bottom: 2px solid {self.accent_color};
        }}

        /* Table Widget */
        QTableWidget {{
            background-color: {self.input_bg};
            color: {self.input_text};
            gridline-color: {self.border_color};
            border: 1px solid {self.border_color};
        }}

        QTableWidget::item {{
            padding: 4px;
        }}

        QTableWidget::item:selected {{
            background-color: {self.accent_color};
            color: {self.button_text};
        }}

        QHeaderView::section {{
            background-color: {self.secondary_bg};
            color: {self.label_text};
            padding: 5px;
            border: 1px solid {self.border_color};
            font-weight: bold;
        }}

        /* Message Box */
        QMessageBox {{
            background-color: {self.primary_bg};
        }}
        """


# Light Theme
LIGHT_THEME = ModernTheme(
    # Primary colors
    primary_bg="#FFFFFF",
    primary_text="#1F2937",
    secondary_bg="#F3F4F6",
    secondary_text="#6B7280",
    # UI elements
    button_bg="#3B82F6",
    button_text="#FFFFFF",
    button_hover="#2563EB",
    button_pressed="#1D4ED8",
    button_disabled="#D1D5DB",
    # Input fields
    input_bg="#F9FAFB",
    input_text="#1F2937",
    input_border="#E5E7EB",
    input_focus_border="#3B82F6",
    # Status
    success_color="#10B981",
    error_color="#EF4444",
    warning_color="#F59E0B",
    info_color="#3B82F6",
    # Sidebar
    sidebar_bg="#F8F9FA",
    sidebar_text="#1F2937",
    sidebar_hover="#E5E7EB",
    sidebar_active="#3B82F6",
    # Other
    border_color="#D1D5DB",
    shadow_color="#00000010",
    label_text="#374151",
    accent_color="#3B82F6",
)

# Dark Theme
DARK_THEME = ModernTheme(
    # Primary colors
    primary_bg="#1F2937",
    primary_text="#F3F4F6",
    secondary_bg="#111827",
    secondary_text="#D1D5DB",
    # UI elements
    button_bg="#3B82F6",
    button_text="#FFFFFF",
    button_hover="#2563EB",
    button_pressed="#1D4ED8",
    button_disabled="#4B5563",
    # Input fields
    input_bg="#374151",
    input_text="#F3F4F6",
    input_border="#4B5563",
    input_focus_border="#60A5FA",
    # Status
    success_color="#34D399",
    error_color="#F87171",
    warning_color="#FBBF24",
    info_color="#60A5FA",
    # Sidebar
    sidebar_bg="#111827",
    sidebar_text="#F3F4F6",
    sidebar_hover="#374151",
    sidebar_active="#3B82F6",
    # Other
    border_color="#4B5563",
    shadow_color="#00000040",
    label_text="#D1D5DB",
    accent_color="#3B82F6",
)


def get_theme(theme_name: str) -> ModernTheme:
    """Get theme by name."""
    themes = {
        "light": LIGHT_THEME,
        "dark": DARK_THEME,
    }
    return themes.get(theme_name, LIGHT_THEME)


def get_stylesheet(theme_name: str) -> str:
    """Get stylesheet for theme."""
    theme = get_theme(theme_name)
    return theme.get_stylesheet()
