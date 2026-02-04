import json
import sys
import os
import subprocess
import signal
import traceback

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QFileDialog,
    QTabWidget, QListWidget, QMessageBox, QStatusBar, QToolBar,
    QComboBox, QScrollArea, QListWidgetItem, QSizePolicy, QAction, QDialog
)

from PyQt5.QtGui  import QIcon, QDesktopServices
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtCore import QObject, QThread, pyqtSignal

import article_introduction_generator.about as about
import article_introduction_generator.modules.configure as configure 
from   article_introduction_generator.modules.wabout  import show_about_window
from   article_introduction_generator.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu


from article_introduction_generator.modules.consult import consultation_in_depth

# ---------- Path to config file ----------
CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            "config.json" )

DEFAULT_CONTENT={   "toolbar_llm_conf": "LLM Conf.",
                    "toolbar_llm_conf_tooltip": "Open the configure Json file of LLM",
                    "toolbar_url_usage": "LLM Usage",
                    "toolbar_url_usage_tooltip": "Open the web page that shows the data usage and cost.",
                    "toolbar_configure": "Configure",
                    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
                    "toolbar_about": "About",
                    "toolbar_about_tooltip": "About the program",
                    "toolbar_coffee": "Coffee",
                    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
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
                        title_message = "An error occurred:", 
                        width = 800,
                        height = 600 ):
    dialog = MessageDialog( message, 
                            window_title = "Error message", 
                            title_message = title_message,
                            button_ok_text = "OK",
                            button_copy_text = "Copy to clipboard",
                            width = width,
                            height = height
    )
    
    dialog.exec_()
    
def show_info_dialog(   message, 
                        title_message = "", 
                        width = 800,
                        height = 600 ):
    dialog = MessageDialog( message, 
                            window_title = "Information message", 
                            title_message = title_message,
                            button_ok_text = "OK",
                            button_copy_text = "Copy to clipboard",
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
        
        placeholder = QListWidgetItem("Click 'Add' to insert a new entry")
        placeholder.setFlags(Qt.NoItemFlags)  # não selecionável / não editável
        placeholder.setForeground(Qt.gray)
        self.list.addItem(placeholder)

        self.list.setToolTip(tooltip)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add")
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        remove_btn = QPushButton("Remove")
        remove_btn.setIcon(QIcon.fromTheme("list-remove"))
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
        placeholder = QListWidgetItem("Click 'Add' to insert a new entry")
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
        base_dir_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_dir_path, 'icons', 'logo.png')
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
        self.load_action = QAction(QIcon.fromTheme("document-open"), "Load JSON", self)
        self.load_action.setToolTip("load JSON")
        self.load_action.triggered.connect(self.load_json)
        self.toolbar.addAction(self.load_action)
        
        #
        self.save_as_action = QAction(QIcon.fromTheme("document-save-as"), "Save as JSON", self)
        self.save_as_action.setToolTip("save as")
        self.save_as_action.triggered.connect(self.save_as_json)
        self.toolbar.addAction(self.save_as_action)
        
        #
        self.generate_intro_action = QAction(QIcon.fromTheme("emblem-generic"), "Generate intro.", self)
        self.generate_intro_action.setToolTip("Generate introduction")
        self.generate_intro_action.triggered.connect(self.generate_intro)
        self.toolbar.addAction(self.generate_intro_action)
        
        # Adicionar o espaçador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        
        #
        self.llm_conf_action = QAction(QIcon.fromTheme("document-properties"), CONFIG["toolbar_llm_conf"], self)
        self.llm_conf_action.setToolTip(CONFIG["toolbar_llm_conf_tooltip"])
        self.llm_conf_action.triggered.connect(self.open_llm_conf_editor)
        self.toolbar.addAction(self.llm_conf_action)
        
        #
        self.url_usage_action = QAction(QIcon.fromTheme("emblem-web"), CONFIG["toolbar_url_usage"], self)
        self.url_usage_action.setToolTip(CONFIG["toolbar_url_usage_tooltip"])
        self.url_usage_action.triggered.connect(self.open_url_usage_editor)
        self.toolbar.addAction(self.url_usage_action)
        
        #
        self.configure_action = QAction(QIcon.fromTheme("document-properties"), CONFIG["toolbar_configure"], self)
        self.configure_action.setToolTip(CONFIG["toolbar_configure_tooltip"])
        self.configure_action.triggered.connect(self.open_configure_editor)
        self.toolbar.addAction(self.configure_action)
        
        #
        self.about_action = QAction(QIcon.fromTheme("help-about"), CONFIG["toolbar_about"], self)
        self.about_action.setToolTip(CONFIG["toolbar_about_tooltip"])
        self.about_action.triggered.connect(self.open_about)
        self.toolbar.addAction(self.about_action)
        
        # Coffee
        self.coffee_action = QAction(QIcon.fromTheme("emblem-favorite"), CONFIG["toolbar_coffee"], self)
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
        self.tabs.addTab(self._wrap_scroll(self._paper_profile_tab()), "Paper Profile")
        self.tabs.addTab(self._wrap_scroll(self._research_problem_tab()), "Research Problem")
        self.tabs.addTab(self._wrap_scroll(self._contributions_tab()), "Contributions")
        self.tabs.addTab(self._related_work_tab(), "Related Work")
        self.tabs.addTab(self._wrap_scroll(self._writing_guidelines_tab()), "Writing Guidelines")
        
        self.tabs.currentChanged.connect(self._on_tab_changed)


    # ---------- Tabs ----------

    def _on_tab_changed(self, index):
        self._save_current_reference()

    def _paper_profile_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.pp_title = LabeledLineEdit(
            "Title",
            "Full paper title."
        )
        self.pp_domain = LabeledLineEdit(
            "Domain",
            "Research domain, e.g., Computer Vision, NLP, Systems."
        )
        self.pp_journal = LabeledLineEdit(
            "Target Journal",
            "Intended journal (IEEE, Elsevier, ACM, etc.)."
        )
        self.pp_keywords = StringListEditor(
            "Keywords",
            "High-level keywords describing the paper."
        )
        self.pp_summary = LabeledTextEdit(
            "Author Intended Summary",
            "Human-written summary describing what the paper does and why."
        )

        for wdg in [self.pp_title, self.pp_domain, self.pp_journal, self.pp_keywords, self.pp_summary]:
            layout.addWidget(wdg)

        w.setLayout(layout)
        return w

    def _research_problem_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.rp_overview = LabeledTextEdit(
            "Research Domain Overview",
            "General overview of the research domain and its importance."
        )
        self.rp_specific = LabeledTextEdit(
            "Specific Problem",
            "Precise formulation of the problem addressed."
        )
        self.rp_challenges = StringListEditor(
            "Practical Challenges",
            "Key practical or theoretical challenges."
        )
        self.rp_insufficient = LabeledTextEdit(
            "Why Existing Solutions Are Insufficient",
            "High-level human assessment without citing specific papers."
        )

        for wdg in [self.rp_overview, self.rp_specific, self.rp_challenges, self.rp_insufficient]:
            layout.addWidget(wdg)

        w.setLayout(layout)
        return w

    def _contributions_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.contributions = StringListEditor(
            "Contributions",
            "Main contributions of the paper, one per entry."
        )

        layout.addWidget(self.contributions)
        w.setLayout(layout)
        return w

    def _related_work_tab(self):
        tabs = QTabWidget()
        tabs.addTab(self._references_tab(), "References")
        tabs.addTab(self._wrap_scroll(self._synthesis_tab()), "Human Curated Synthesis")
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

        self.ref_bibtex = LabeledTextEdit("BibTeX", "BibTeX entry. This is the only source for citations.")
        self.ref_abstract = LabeledTextEdit("Abstract", "Original abstract of the cited paper.")
        self.ref_category = LabeledLineEdit("Methodological Category", "e.g., deep_learning, transformer_based, graph_based.")
        self.ref_contribution = LabeledTextEdit("Central Technical Idea", "Main technical idea introduced by this work.")
        self.ref_strengths = StringListEditor("Author Reported Strengths", "Strengths explicitly claimed by the original authors.")
        self.ref_limitations = StringListEditor("Reported Limitations", "Limitations discussed or implied by the paper.")
        self.ref_relevance = LabeledTextEdit("Relevance to Our Work", "How this work relates to and differs from our paper.")
        self.ref_role = LabeledLineEdit("Introduction Paragraph Role", "foundational, early_state_of_art, recent_advances, etc.")

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

        add = QPushButton("Add Reference")
        add.setIcon(QIcon.fromTheme("list-add"))
        add.setIconSize(QSize(32, 32))

        remove = QPushButton("Remove Reference")
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
            QMessageBox.warning(self, "Invalid name", "Reference key cannot be empty.")
            self.ref_list.blockSignals(True)
            item.setText(old_key)
            self.ref_list.blockSignals(False)
            return

        if new_key in self.references_data and new_key != old_key:
            QMessageBox.warning(self, "Duplicate key", "This reference key already exists.")
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

        self.syn_trends = StringListEditor(
            "Common Trends",
            "Observed trends across the literature."
        )
        self.syn_open = StringListEditor(
            "Open Problems",
            "Unresolved problems identified by the author."
        )
        self.syn_gap = LabeledTextEdit(
            "Explicit Research Gap",
            "Clear formulation of the research gap addressed by the paper."
        )

        for wdg in [self.syn_trends, self.syn_open, self.syn_gap]:
            layout.addWidget(wdg)

        w.setLayout(layout)
        return w

    def _writing_guidelines_tab(self):
        w = QWidget()
        layout = QVBoxLayout()

        self.wg = LabeledTextEdit(
            "Writing Guidelines",
            "Explicit instructions to be followed by the LLM when generating text."
        )

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

        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON Files (*.json)")
        if not path:
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.current_path = path
        self.status.showMessage(f"Loaded from {path}")

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
        
    def save_as_json(self):

        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if not path:
            return

        data = self._obtaining_data()

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.current_path = path
        self.status.showMessage(f"Saved to {path}")

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

    def generate_intro(self):
        global CONFIG_LLM
        
        data = self._obtaining_data()

        if self.is_data_empty(data):
            QMessageBox.warning(
                self,
                "Missing data",
                "Please fill at least one relevant field before generating the introduction."
            )
            return

        if CONFIG_LLM["api_key"]=="":
            CONFIG_LLM = configure.load_config(CONFIG_LLM_PATH)
            
            if CONFIG_LLM["api_key"]=="":
                self.status.showMessage("Open: " + CONFIG_LLM_PATH)
                self._open_file_in_text_editor(CONFIG_LLM_PATH)
                QDesktopServices.openUrl(QUrl(CONFIG_LLM["usage"]))
                
                return

        # Feedback visual
        self.status.showMessage("Consulting LLM… please wait")
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
        self.status.showMessage("Done")
        show_info_dialog(out, title_message="LLM response:")

    def on_intro_error(self, error_msg):
        self.generate_intro_action.setEnabled(True)
        self.status.showMessage("Error")
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

