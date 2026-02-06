import json
import sys
import os
import subprocess
import signal
import traceback

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QFileDialog, QFrame, 
    QTabWidget, QListWidget, QMessageBox, QStatusBar, QToolBar,
    QComboBox, QScrollArea, QListWidgetItem, QSizePolicy, QAction, QDialog
)

from PyQt5.QtGui  import QIcon, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtCore import QObject, QThread, pyqtSignal

import article_introduction_generator.about as about
import article_introduction_generator.modules.configure as configure 
from   article_introduction_generator.modules.resources import resource_path
from   article_introduction_generator.modules.wabout    import show_about_window
from   article_introduction_generator.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu

from article_introduction_generator.modules.consult import consultation_in_depth, consultation_in_text

# ---------- Path to config file ----------
CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            "config.json" )

DEFAULT_CONTENT={   
    "toolbar_load_json": "Load JSON",
    "toolbar_load_json_tooltip": "Load data from a JSON file with the *.intro.json extension.",
    "toolbar_save_as": "Save as JSON",
    "toolbar_save_as_tooltip": "Save all data as a JSON file with the extension *.intro.json.",
    "toolbar_gen_intro": "Generate intro.",
    "toolbar_gen_intro_tooltip": "Generate an introduction using an LLM API key. Before using this button, you need to configure your LLM API key.",
    "toolbar_gen_prompt": "Generate prompt",
    "toolbar_gen_prompt_tooltip": "Generate only the query message (prompt). You don’t need to provide an API key or configure the LLM. This prompt can be pasted into any preferred LLM chat interface.",
    "toolbar_llm_conf": "LLM Conf.",
    "toolbar_llm_conf_tooltip": "Open the configure Json file of LLM.",
    "toolbar_url_usage": "LLM Usage",
    "toolbar_url_usage_tooltip": "Open the web page that shows the data usage and cost.",
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "tab_paper_profile": "1. Paper Profile",
    "tab_paper_profile_tooltip": "Basic information about the paper",
    "tab_research_problem": "2. Research Problem",
    "tab_research_problem_tooltip": "Define the research problem and motivation of paper",
    "tab_contributions": "3. Contributions",
    "tab_contributions_tooltip": "Main scientific contributions of paper",
    "tab_related_work": "4. Related Work",
    "tab_related_work_tooltip": "Related works and literature review",
    "tab_writing_guidelines": "5. LLM writing Guidelines",
    "tab_writing_guidelines_tooltip": "Writing rules and formatting guidelines in LLM introduction generation",
    "profile_title": "Title",
    "profile_title_tooltip": "Full paper title.",
    "profile_domain": "Domain",
    "profile_domain_tooltip": "Research domain, e.g., Computer Vision, NLP, Systems.",
    "profile_journal": "Target Journal",
    "profile_journal_tooltip": "Intended journal (IEEE, Elsevier, ACM, etc.).",
    "profile_keywords": "Keywords",
    "profile_keywords_tooltip": "High-level keywords describing the paper.",
    "profile_summary": "Author Intended Summary",
    "profile_summary_tooltip": "Human-written summary describing what the paper does and why.",
    "research_overview": "Research Domain Overview",
    "research_overview_tooltip": "General overview of the research domain and its importance.",
    "research_specific": "Specific Problem",
    "research_specific_tooltip": "Precise formulation of the problem addressed.",
    "research_challenges": "Practical Challenges",
    "research_challenges_tooltip": "Key practical or theoretical challenges.",
    "research_insufficient": "Why Existing Solutions Are Insufficient",
    "research_insufficient_tooltip": "High-level human assessment without citing specific papers.",
    "contributions_list": "Contributions",
    "contributions_list_tooltip": "Main contributions of the paper, one per entry.",
    "related_references": "References",
    "related_references_tooltip": "References used in the article" ,
    "related_references_bibtex": "BibTeX", 
    "related_references_bibtex_tooltip": "BibTeX entry. This is the only source for citations.",
    "related_references_abstract": "Abstract",
    "related_references_abstract_tooltip": "Original abstract of the cited paper.",
    "related_references_methodological": "Methodological Category", 
    "related_references_methodological_tooltip": "e.g., deep_learning, transformer_based, graph_based.",
    "related_references_idea": "Central Technical Idea", 
    "related_references_idea_tooltip": "Main technical idea introduced by this work.",
    "related_references_strengths": "Author Reported Strengths", 
    "related_references_strengths_tooltip": "Strengths explicitly claimed by the original authors.",
    "related_references_limitations": "Reported Limitations", 
    "related_references_limitations_tooltip": "Limitations discussed or implied by the paper.",
    "related_references_relevance": "Relevance to Our Work", 
    "related_references_relevance_tooltip": "How this work relates to and differs from our paper.",
    "related_references_role": "Introduction Paragraph Role", 
    "related_references_role_tooltip": "foundational, early_state_of_art, recent_advances, etc.",
    "related_references_add": "Add Reference",
    "related_references_remove": "Remove Reference",
    "related_references_invalid_key": "Invalid name",
    "related_references_invalid_key_tip": "Reference key cannot be empty.",
    "related_references_duplicate_key": "Duplicate key",
    "related_references_duplicate_key_tip": "This reference key already exists.",
    "related_synthesis": "Human Curated Synthesis",
    "related_synthesis_tooltip": "Synthesis of your trends and observations from the references",
    "related_synthesis_trends": "Common Trends",
    "related_synthesis_trends_tooltip": "Observed trends across the literature.",
    "related_synthesis_problems": "Open Problems",
    "related_synthesis_problems_tooltip": "Unresolved problems identified by the author.",
    "related_synthesis_gaps": "Explicit Research Gap",
    "related_synthesis_gaps_tooltip": "Clear formulation of the research gap addressed by the paper.",
    "guidelines_entry": "Writing Guidelines",
    "guidelines_entry_tooltip": "Explicit instructions to be followed by the LLM when generating text.",
    "error_missing_data": "Missing data",
    "error_missing_data_msg": "Please fill at least one relevant field before generating the introduction.",
    "message_error": "Error",
    "message_information": "Information",
    "message_done": "Done",
    "message_open": "Open",
    "message_prompt": "Prompt",
    "message_saved_to": "Saved to",
    "message_loaded_from": "Loaded from",
    "message_llm_response": "LLM response",
    "message_llm_consulting": "Consulting LLM… please wait",
    "message_dialog_error": "An error occurred",
    "message_dialog_information": "Information message",
    "message_dialog_ok": "OK",
    "message_dialog_copy_clipboard": "Copy to clipboard",
    "list_editor_placeholder": "Click 'Add' to insert a new entry",
    "list_editor_add": "Add",
    "list_editor_add_tooltip": "Add an element to the list",
    "list_editor_remove": "Remove",
    "list_editor_remove_tooltip": "Remove an element to the list",
    "window_width": 1024,
    "window_height": 800
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)

# ---------- Path to config LLM file ----------
CONFIG_LLM_PATH = os.path.join( os.path.expanduser("~"),
                                ".config", 
                                about.__package__, 
                                "config.llm.json" )

DEFAULT_LLM_CONTENT={
    "api_key": "",
    "usage": "https://deepinfra.com/dash/usage",
    "base_url": "https://api.deepinfra.com/v1/openai",
    "model": "meta-llama/Meta-Llama-3.1-70B-Instruct"
}

configure.verify_default_config(CONFIG_LLM_PATH,default_content=DEFAULT_LLM_CONTENT)

CONFIG_LLM = configure.load_config(CONFIG_LLM_PATH)


# -------- Worker --------
class ConsultationWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, config, data):
        super().__init__()
        self.config = config
        self.data = data

    def run(self):
        try:
            result = consultation_in_depth(self.config, self.data)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# -------- Error dialog --------
class MessageDialog(QDialog):
    """Error dialog with scrollable text area"""
    def __init__(   self, 
                    message, 
                    parent=None, 
                    window_title = "Title message",
                    title_message = "Some text",
                    button_ok_text = "OK",
                    button_copy_text = "Copy to clipboard",
                    width = 400,
                    height = 300
        ):
        
        super().__init__(parent)

        self.setWindowTitle(window_title)
        self.resize(width, height)

        # Layout principal
        layout = QVBoxLayout(self)

        # Label
        label = QLabel(title_message)
        layout.addWidget(label)

        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(message)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        layout.addWidget(self.text_edit)

        # Layout dos botões
        button_layout = QHBoxLayout()

        # Botão copiar
        copy_button = QPushButton(button_copy_text)
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)

        # Botão OK
        ok_button = QPushButton(button_ok_text)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())

def show_error_dialog(  message, 
                        title_message = CONFIG["message_dialog_error"], 
                        width = 800,
                        height = 600 ):
    dialog = MessageDialog( message, 
                            window_title = CONFIG["message_error"], 
                            title_message = title_message,
                            button_ok_text = CONFIG["message_dialog_ok"],
                            button_copy_text = CONFIG["message_dialog_copy_clipboard"],
                            width = width,
                            height = height
    )
    
    dialog.exec_()
    
def show_info_dialog(   message, 
                        title_message = CONFIG["message_dialog_information"], 
                        width = 800,
                        height = 600 ):
    dialog = MessageDialog( message, 
                            window_title = CONFIG["message_information"], 
                            title_message = title_message,
                            button_ok_text = CONFIG["message_dialog_ok"],
                            button_copy_text = CONFIG["message_dialog_copy_clipboard"],
                            width = width,
                            height = height
    )
    
    dialog.exec_()

# ---------- Reusable Widgets ----------

class LabeledTextEdit(QWidget):
    def __init__(self, label, tooltip=""):
        super().__init__()
        layout = QHBoxLayout()
        self.label = QLabel(label)
        self.text = QTextEdit()
        self.text.setToolTip(tooltip)
        self.text.setMinimumHeight(80)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.text, 4)
        self.setLayout(layout)

    def get(self):
        return self.text.toPlainText().strip()

    def set(self, value):
        self.text.setPlainText(value or "")


class LabeledLineEdit(QWidget):
    def __init__(self, label, tooltip=""):
        super().__init__()
        layout = QHBoxLayout()
        self.label = QLabel(label)
        self.line = QLineEdit()
        self.line.setToolTip(tooltip)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.line, 4)
        self.setLayout(layout)

    def get(self):
        return self.line.text().strip()

    def set(self, value):
        self.line.setText(value or "")


class StringListEditor(QWidget):
    def __init__(self, label, tooltip=""):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel(label)
        title.setToolTip(tooltip)
        self.list = QListWidget()
        
        placeholder = QListWidgetItem(CONFIG["list_editor_placeholder"])
        placeholder.setFlags(Qt.NoItemFlags)  # não selecionável / não editável
        placeholder.setForeground(Qt.gray)
        self.list.addItem(placeholder)

        self.list.setToolTip(tooltip)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton(CONFIG["list_editor_add"])
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setToolTip(CONFIG["list_editor_add_tooltip"])
        remove_btn = QPushButton(CONFIG["list_editor_remove"])
        remove_btn.setIcon(QIcon.fromTheme("list-remove"))
        remove_btn.setToolTip(CONFIG["list_editor_remove_tooltip"])
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)

        add_btn.clicked.connect(self.add_item)
        remove_btn.clicked.connect(self.remove_item)

        layout.addWidget(title)
        layout.addWidget(self.list)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.list.setEditTriggers(
            self.list.DoubleClicked | self.list.SelectedClicked
        )

    def add_item(self, text=None):
        from PyQt5.QtWidgets import QListWidgetItem

        # Se o primeiro item for placeholder, remove
        if self.list.count() == 1:
            item0 = self.list.item(0)
            if item0.flags() == Qt.NoItemFlags:
                self.list.clear()


        if not isinstance(text, str):
            text = ""

        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.list.addItem(item)
        self.list.editItem(item)


    def remove_item(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

        if self.list.count() == 0:
            self._add_placeholder()


    def get(self):
        values = []
        for i in range(self.list.count()):
            item = self.list.item(i)
            if not (item.flags() & Qt.ItemIsEditable):
                continue
            text = item.text().strip()
            if text:
                values.append(text)
        return values


    def set(self, values):
        self.list.clear()

        if not values:
            self._add_placeholder()
            return

        for v in values:
            item = QListWidgetItem(v)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.list.addItem(item)


    def _add_placeholder(self):
        placeholder = QListWidgetItem(CONFIG["list_editor_placeholder"])
        placeholder.setFlags(Qt.NoItemFlags)
        placeholder.setForeground(Qt.gray)
        self.list.addItem(placeholder)



# ---------- Main Window ----------

class JsonIntroductionEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle(about.__program_name__)
        #self.setGeometry(100, 100, 800, 240)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])

        ## Icon
        # Get base directory for icons
        self.icon_path = resource_path('icons', 'logo.png')
        self.setWindowIcon(QIcon(self.icon_path)) 

        self.current_path = None

        self.references_data = {}
        
        self.current_reference_key = None

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._create_toolbar()
        self._create_status_bar()

        self._create_tabs()
        self._apply_styles()


    # ---------- UI ----------
    def _apply_styles(self):
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #999;
                border-radius: 4px;
                background-color: #f9f9f9;
            }

            QListWidget::item {
                padding: 4px;
            }

            QListWidget::item:selected {
                background-color: #cce5ff;
                color: black;
            }

            QTextEdit {
                border: 1px solid #bbb;
                border-radius: 4px;
                background-color: #ffffff;
            }

            QLineEdit {
                border: 1px solid #bbb;
                border-radius: 4px;
                background-color: #ffffff;
                padding: 2px;
            }
            QListWidget:empty {
                background-color: #f9f9f9;
            }

            QListWidget:empty::item {
                color: #999;
            }
        """)

    def _create_toolbar(self):
        self.toolbar = self.addToolBar("Main")
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        #
        self.load_action = QAction( QIcon.fromTheme("document-open"), 
                                    CONFIG["toolbar_load_json"], 
                                    self )
        self.load_action.setToolTip(CONFIG["toolbar_load_json_tooltip"])
        self.load_action.triggered.connect(self.load_json)
        self.toolbar.addAction(self.load_action)
        
        #
        self.save_as_action = QAction(  QIcon.fromTheme("document-save-as"), 
                                        CONFIG["toolbar_save_as"], 
                                        self)
        self.save_as_action.setToolTip(CONFIG["toolbar_save_as_tooltip"])
        self.save_as_action.triggered.connect(self.save_as_json)
        self.toolbar.addAction(self.save_as_action)
        
        #
        self.generate_intro_action = QAction(   QIcon.fromTheme("emblem-generic"), 
                                                CONFIG["toolbar_gen_intro"], 
                                                self)
        self.generate_intro_action.setToolTip(CONFIG["toolbar_gen_intro_tooltip"])
        self.generate_intro_action.triggered.connect(self.generate_intro)
        self.toolbar.addAction(self.generate_intro_action)
        
        #
        self.generate_cmd_action = QAction( QIcon.fromTheme("document-edit"), 
                                            CONFIG["toolbar_gen_prompt"], 
                                            self)
        self.generate_cmd_action.setToolTip(CONFIG["toolbar_gen_prompt_tooltip"])
        self.generate_cmd_action.triggered.connect(self.generate_cmd)
        self.toolbar.addAction(self.generate_cmd_action)
        
        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        
        #
        self.llm_conf_action = QAction( QIcon.fromTheme("document-properties"), 
                                        CONFIG["toolbar_llm_conf"], 
                                        self)
        self.llm_conf_action.setToolTip(CONFIG["toolbar_llm_conf_tooltip"])
        self.llm_conf_action.triggered.connect(self.open_llm_conf_editor)
        self.toolbar.addAction(self.llm_conf_action)
        
        #
        self.url_usage_action = QAction(QIcon.fromTheme("emblem-web"), 
                                        CONFIG["toolbar_url_usage"], 
                                        self)
        self.url_usage_action.setToolTip(CONFIG["toolbar_url_usage_tooltip"])
        self.url_usage_action.triggered.connect(self.open_url_usage_editor)
        self.toolbar.addAction(self.url_usage_action)
        
        # Adicionar o espaçador
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain) # QFrame.Raised # QFrame.Sunken
        self.toolbar.addWidget(separator)
        
        #
        self.configure_action = QAction(QIcon.fromTheme("document-properties"), 
                                        CONFIG["toolbar_configure"], 
                                        self)
        self.configure_action.setToolTip(CONFIG["toolbar_configure_tooltip"])
        self.configure_action.triggered.connect(self.open_configure_editor)
        self.toolbar.addAction(self.configure_action)
        
        #
        self.about_action = QAction(QIcon.fromTheme("help-about"), 
                                    CONFIG["toolbar_about"], 
                                    self)
        self.about_action.setToolTip(CONFIG["toolbar_about_tooltip"])
        self.about_action.triggered.connect(self.open_about)
        self.toolbar.addAction(self.about_action)
        
        # Coffee
        self.coffee_action = QAction(   QIcon.fromTheme("emblem-favorite"), 
                                        CONFIG["toolbar_coffee"], 
                                        self)
        self.coffee_action.setToolTip(CONFIG["toolbar_coffee_tooltip"])
        self.coffee_action.triggered.connect(self.on_coffee_action_click)
        self.toolbar.addAction(self.coffee_action)

    def _open_file_in_text_editor(self, filepath):
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # Linux/macOS
            subprocess.run(['xdg-open', filepath])
    
    def open_url_usage_editor(self):
        QDesktopServices.openUrl(QUrl(CONFIG_LLM["usage"]))
        
    def open_configure_editor(self):
        self._open_file_in_text_editor(CONFIG_PATH)
        
    def open_llm_conf_editor(self):
        self._open_file_in_text_editor(CONFIG_LLM_PATH)

    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)

    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))
    

    def _create_status_bar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def _wrap_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def _create_tabs(self):
        self.tabs.addTab(   self._wrap_scroll(self._paper_profile_tab()), 
                            CONFIG["tab_paper_profile"] )
        self.tabs.addTab(   self._wrap_scroll(self._research_problem_tab()), 
                            CONFIG["tab_research_problem"] )
        self.tabs.addTab(   self._wrap_scroll(self._contributions_tab()), 
                            CONFIG["tab_contributions"] )
        self.tabs.addTab(   self._related_work_tab(), 
                            CONFIG["tab_related_work"] )
        self.tabs.addTab(   self._wrap_scroll(self._writing_guidelines_tab()), 
                            CONFIG["tab_writing_guidelines"] )
        
        self.tabs.setTabToolTip(0, CONFIG["tab_paper_profile_tooltip"])
        self.tabs.setTabToolTip(1, CONFIG["tab_research_problem_tooltip"])
        self.tabs.setTabToolTip(2, CONFIG["tab_contributions_tooltip"])
        self.tabs.setTabToolTip(3, CONFIG["tab_related_work_tooltip"])
        self.tabs.setTabToolTip(4, CONFIG["tab_writing_guidelines_tooltip"])
        
        self.tabs.currentChanged.connect(self._on_tab_changed)

    # ---------- Tabs ----------

    def _on_tab_changed(self, index):
        self._save_current_reference()

    def _paper_profile_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.pp_title    = LabeledLineEdit( CONFIG["profile_title"], 
                                            CONFIG["profile_title_tooltip"] )
        self.pp_domain   = LabeledLineEdit( CONFIG["profile_domain"], 
                                            CONFIG["profile_domain_tooltip"] )
        self.pp_journal  = LabeledLineEdit( CONFIG["profile_journal"], 
                                            CONFIG["profile_journal_tooltip"] )
        self.pp_keywords = StringListEditor(CONFIG["profile_keywords"], 
                                            CONFIG["profile_keywords_tooltip"] )
        self.pp_summary  = LabeledTextEdit( CONFIG["profile_summary"], 
                                            CONFIG["profile_summary_tooltip"] )

        for wdg in [self.pp_title, self.pp_domain, self.pp_journal, self.pp_keywords, self.pp_summary]:
            layout.addWidget(wdg)

        w.setLayout(layout)
        return w

    def _research_problem_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.rp_overview = LabeledTextEdit( CONFIG["research_overview"], 
                                            CONFIG["research_overview_tooltip"] )
        self.rp_specific = LabeledTextEdit( CONFIG["research_specific"], 
                                            CONFIG["research_specific_tooltip"] )
        self.rp_challenges = StringListEditor(  CONFIG["research_challenges"], 
                                                CONFIG["research_challenges_tooltip"] )
        self.rp_insufficient = LabeledTextEdit( CONFIG["research_insufficient"], 
                                                CONFIG["research_insufficient_tooltip"] )

        for wdg in [self.rp_overview, self.rp_specific, self.rp_challenges, self.rp_insufficient]:
            layout.addWidget(wdg)

        w.setLayout(layout)
        return w

    def _contributions_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.contributions = StringListEditor(  CONFIG["contributions_list"], 
                                                CONFIG["contributions_list_tooltip"])

        layout.addWidget(self.contributions)
        w.setLayout(layout)
        return w

    def _related_work_tab(self):
        tabs = QTabWidget()
        tabs.addTab(self._references_tab(), 
                    CONFIG["related_references"] )
        tabs.addTab(self._wrap_scroll(self._synthesis_tab()), 
                    CONFIG["related_synthesis"] )
        
        tabs.setTabToolTip(0, CONFIG["related_references_tooltip"])
        tabs.setTabToolTip(1, CONFIG["related_synthesis_tooltip"])
        
        return tabs

    def _references_tab(self):
        w = QWidget()
        main_layout = QVBoxLayout(w)

        # ---- Lista de referências + painel de edição ----
        content_layout = QHBoxLayout()

        # Lista de referências
        self.ref_list = QListWidget()
        self.ref_list.setEditTriggers(
            QListWidget.DoubleClicked | QListWidget.EditKeyPressed
        )
        self.ref_list.itemChanged.connect(self._on_reference_renamed)
        self.ref_list.currentItemChanged.connect(self._load_reference)
        content_layout.addWidget(self.ref_list, 1)

        # Painel de edição (scrollable)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.ref_bibtex = LabeledTextEdit(  CONFIG["related_references_bibtex"], 
                                            CONFIG["related_references_bibtex_tooltip"] )
        self.ref_abstract = LabeledTextEdit(CONFIG["related_references_abstract"], 
                                            CONFIG["related_references_abstract_tooltip"] )
        self.ref_category = LabeledLineEdit(CONFIG["related_references_methodological"], 
                                            CONFIG["related_references_methodological_tooltip"] )
        self.ref_contribution = LabeledTextEdit(CONFIG["related_references_idea"], 
                                                CONFIG["related_references_idea_tooltip"] )
        self.ref_strengths = StringListEditor(  CONFIG["related_references_strengths"], 
                                                CONFIG["related_references_strengths_tooltip"] )
        self.ref_limitations = StringListEditor(CONFIG["related_references_limitations"], 
                                                CONFIG["related_references_limitations_tooltip"] )
        self.ref_relevance = LabeledTextEdit(   CONFIG["related_references_relevance"], 
                                                CONFIG["related_references_relevance_tooltip"] )
        self.ref_role = LabeledLineEdit(CONFIG["related_references_role"], 
                                        CONFIG["related_references_role_tooltip"] )

        for wdg in [
            self.ref_bibtex, self.ref_abstract, self.ref_category,
            self.ref_contribution, self.ref_strengths,
            self.ref_limitations, self.ref_relevance, self.ref_role
        ]:
            right_layout.addWidget(wdg)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(right_widget)

        content_layout.addWidget(scroll, 3)

        main_layout.addLayout(content_layout)

        # ---- Botões fora do scroll ----
        btns = QHBoxLayout()

        add = QPushButton(CONFIG["related_references_add"])
        add.setIcon(QIcon.fromTheme("list-add"))
        add.setIconSize(QSize(32, 32))

        remove = QPushButton(CONFIG["related_references_remove"])
        remove.setIcon(QIcon.fromTheme("list-remove"))
        remove.setIconSize(QSize(32, 32))

        btns.addWidget(add)
        btns.addWidget(remove)

        add.clicked.connect(self._add_reference)
        remove.clicked.connect(self._remove_reference)

        main_layout.addLayout(btns)

        w.setLayout(main_layout)
        return w

    
    
    def _on_reference_renamed(self, item: QListWidgetItem):
        old_key = self.current_reference_key
        new_key = item.text().strip()

        if not old_key:
            return

        if not new_key:
            QMessageBox.warning(self, 
                                CONFIG["related_references_invalid_key"], 
                                CONFIG["related_references_invalid_key_tip"])
            self.ref_list.blockSignals(True)
            item.setText(old_key)
            self.ref_list.blockSignals(False)
            return

        if new_key in self.references_data and new_key != old_key:
            QMessageBox.warning(self, 
                                CONFIG["related_references_duplicate_key"], 
                                CONFIG["related_references_duplicate_key_tip"])
            self.ref_list.blockSignals(True)
            item.setText(old_key)
            self.ref_list.blockSignals(False)
            return

        self._save_current_reference()

        self.references_data[new_key] = self.references_data.pop(old_key)
        self.current_reference_key = new_key


    def _synthesis_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.syn_trends = StringListEditor( CONFIG["related_synthesis_trends"], 
                                            CONFIG["related_synthesis_trends_tooltip"] )
        self.syn_open = StringListEditor(   CONFIG["related_synthesis_problems"],
                                            CONFIG["related_synthesis_problems_tooltip"] )
        self.syn_gap = LabeledTextEdit( CONFIG["related_synthesis_gaps"],
                                        CONFIG["related_synthesis_gaps_tooltip"] )

        for wdg in [self.syn_trends, self.syn_open, self.syn_gap]:
            layout.addWidget(wdg)

        w.setLayout(layout)
        return w

    def _writing_guidelines_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.wg = LabeledTextEdit( CONFIG["guidelines_entry"], CONFIG["guidelines_entry_tooltip"] )

        layout.addWidget(self.wg)
        w.setLayout(layout)
        return w

    # ---------- Reference Helpers ----------

    def _add_reference(self):
        if self.references_data:
            indices = []
            for k in self.references_data.keys():
                try:
                    indices.append(int(k.split("_")[1]))
                except (IndexError, ValueError):
                    pass
            next_idx = max(indices) + 1 if indices else 1
        else:
            next_idx = 1

        key = f"ref_{next_idx}"
        self.references_data[key] = {}

        self.ref_list.blockSignals(True)

        item = QListWidgetItem(key)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.ref_list.addItem(item)
        self.ref_list.setCurrentItem(item)

        self.current_reference_key = key

        self.ref_list.blockSignals(False)

        self._clear_reference_editor()

    def _clear_reference_editor(self):
        self.ref_bibtex.set("")
        self.ref_abstract.set("")
        self.ref_category.set("")
        self.ref_contribution.set("")
        self.ref_strengths.set([])
        self.ref_limitations.set([])
        self.ref_relevance.set("")
        self.ref_role.set("")

    def _remove_reference(self):
        for item in self.ref_list.selectedItems():
            key = item.text()
            self.references_data.pop(key, None)
            self.ref_list.takeItem(self.ref_list.row(item))

            if key == self.current_reference_key:
                self.current_reference_key = None

        self._clear_reference_editor()

    def _save_current_reference(self):
        if not self.current_reference_key:
            return

        self.references_data[self.current_reference_key] = {
            "bibtex": self.ref_bibtex.get(),
            "abstract": self.ref_abstract.get(),
            "methodological_category": self.ref_category.get(),
            "central_technical_idea": self.ref_contribution.get(),
            "author_reported_strengths": self.ref_strengths.get(),
            "reported_limitations": self.ref_limitations.get(),
            "relevance_to_our_work": self.ref_relevance.get(),
            "introduction_paragraph_role": self.ref_role.get(),
        }


    def _load_reference(self, current, previous):
        if previous and self.current_reference_key:
            self._save_current_reference()

        if not current:
            self.current_reference_key = None
            return

        self.ref_list.blockSignals(True)

        self.current_reference_key = current.text()
        ref = self.references_data.get(self.current_reference_key, {})

        self.ref_bibtex.set(ref.get("bibtex"))
        self.ref_abstract.set(ref.get("abstract"))
        self.ref_category.set(ref.get("methodological_category"))
        self.ref_contribution.set(ref.get("central_technical_idea"))
        self.ref_strengths.set(ref.get("author_reported_strengths", []))
        self.ref_limitations.set(ref.get("reported_limitations", []))
        self.ref_relevance.set(ref.get("relevance_to_our_work"))
        self.ref_role.set(ref.get("introduction_paragraph_role"))

        self.ref_list.blockSignals(False)


    # ---------- Load / Save ----------

    def load_json(self):
        self._save_current_reference()

        path, _ = QFileDialog.getOpenFileName(self, CONFIG["toolbar_load_json"], "", "JSON Files (*.intro.json)")
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.current_path = path
        self.status.showMessage(CONFIG["message_loaded_from"]+": "+path)

        # ---- Paper Profile ----
        pp = data.get("paper_profile", {})
        self.pp_title.set(pp.get("title"))
        self.pp_domain.set(pp.get("domain"))
        self.pp_journal.set(pp.get("target_journal"))
        self.pp_keywords.set(pp.get("keywords", []))
        self.pp_summary.set(pp.get("author_intended_summary"))

        # ---- Research Problem ----
        rp = data.get("research_problem", {})
        self.rp_overview.set(rp.get("research_domain_overview"))
        self.rp_specific.set(rp.get("specific_problem"))
        self.rp_challenges.set(rp.get("practical_challenges", []))
        self.rp_insufficient.set(rp.get("why_existing_solutions_are_insufficient"))

        # ---- Contributions ----
        self.contributions.set(data.get("contributions", []))

        # ---- Writing Guidelines ----
        self.wg.set(data.get("writing_guidelines", ""))

        # ---- Related Work: References ----
        self.references_data = data.get("related_work", {}).get("references", {})
        self.ref_list.clear()

        for key in self.references_data.keys():
            item = QListWidgetItem(key)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.ref_list.addItem(item)

        if self.ref_list.count() > 0:
            self.ref_list.setCurrentRow(0)

        # ---- Related Work: Human Curated Synthesis ----
        synth = data.get("related_work", {}).get("human_curated_synthesis", {})
        self.syn_trends.set(synth.get("common_trends", []))
        self.syn_open.set(synth.get("open_problems", []))
        self.syn_gap.set(synth.get("explicit_research_gap"))

    def _obtaining_data(self):
        self._save_current_reference()

        data = {
            "paper_profile": {
                "title": self.pp_title.get(),
                "domain": self.pp_domain.get(),
                "target_journal": self.pp_journal.get(),
                "keywords": self.pp_keywords.get(),
                "author_intended_summary": self.pp_summary.get()
            },
            "research_problem": {
                "research_domain_overview": self.rp_overview.get(),
                "specific_problem": self.rp_specific.get(),
                "practical_challenges": self.rp_challenges.get(),
                "why_existing_solutions_are_insufficient": self.rp_insufficient.get()
            },
            "contributions": self.contributions.get(),
            "related_work": {
                "references": self.references_data,
                "human_curated_synthesis": {
                    "common_trends": self.syn_trends.get(),
                    "open_problems": self.syn_open.get(),
                    "explicit_research_gap": self.syn_gap.get()
                }
            },
            "writing_guidelines": self.wg.get()
        }
        
        return data

    def ensure_intro_json(self, path: str) -> str:
        if path.endswith(".intro.json"):
            return path
        elif path.endswith(".json"):
            return path[:-5] + ".intro.json"  # remove ".json"
        else:
            return path + ".intro.json"

    def save_as_json(self):

        path, _ = QFileDialog.getSaveFileName(self, CONFIG["toolbar_save_as"], "", "JSON Files (*.intro.json)")
        if not path:
            return
        
        path = self.ensure_intro_json(path)
        
        data = self._obtaining_data()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.current_path = path
        self.status.showMessage(CONFIG["message_saved_to"]+": "+path)

    def is_data_empty(self, data: dict) -> bool:
        def has_content(value):
            if isinstance(value, str):
                return bool(value.strip())
            if isinstance(value, list):
                return any(has_content(v) for v in value)
            if isinstance(value, dict):
                return any(has_content(v) for v in value.values())
            return False

        return not has_content(data)

    def generate_cmd(self):
        data = self._obtaining_data()

        if self.is_data_empty(data):
            QMessageBox.warning(
                self,
                CONFIG["error_missing_data"],
                CONFIG["error_missing_data_msg"]
            )
            return
            
        prompt = consultation_in_text(data)
        
        show_info_dialog(   prompt, 
                        title_message = CONFIG["message_prompt"], 
                        width = 800,
                        height = 600 )
    
    def generate_intro(self):
        global CONFIG_LLM
        
        data = self._obtaining_data()

        if self.is_data_empty(data):
            QMessageBox.warning(
                self,
                CONFIG["error_missing_data"],
                CONFIG["error_missing_data_msg"]
            )
            return

        if CONFIG_LLM["api_key"]=="":
            CONFIG_LLM = configure.load_config(CONFIG_LLM_PATH)
            
            if CONFIG_LLM["api_key"]=="":
                self.status.showMessage(CONFIG["message_open"]+": " + CONFIG_LLM_PATH)
                self._open_file_in_text_editor(CONFIG_LLM_PATH)
                QDesktopServices.openUrl(QUrl(CONFIG_LLM["usage"]))
                
                return

        # Feedback visual
        self.status.showMessage(CONFIG["message_llm_consulting"])
        self.generate_intro_action.setEnabled(False)
        
        # Thread
        self.thread = QThread()
        self.worker = ConsultationWorker(CONFIG_LLM, data)

        self.worker.moveToThread(self.thread)

        # Conexões
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_intro_ready)
        self.worker.error.connect(self.on_intro_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_intro_ready(self, out):
        self.generate_intro_action.setEnabled(True)
        self.status.showMessage(CONFIG["message_done"])
        show_info_dialog(out, title_message=CONFIG["message_llm_response"]+": ")

    def on_intro_error(self, error_msg):
        self.generate_intro_action.setEnabled(True)
        self.status.showMessage(CONFIG["message_error"])
        show_error_dialog(error_msg)

# ---------- Main ----------

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"), 
                        program_name=about.__program_name__)
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".config","autostart"), 
                                overwrite=True, 
                                program_name=about.__program_name__)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".local","share","applications"), 
                                overwrite=True, 
                                program_name=about.__program_name__)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 
    
    win = JsonIntroductionEditor()
    win.show()
    sys.exit(app.exec_())
    
    
if __name__ == "__main__":
    main()

