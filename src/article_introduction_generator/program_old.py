import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QPushButton, QFileDialog,
    QTabWidget, QListWidget, QMessageBox, QStatusBar, QToolBar,
    QComboBox, QScrollArea, QListWidgetItem
)
from PyQt5.QtCore import Qt


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
        remove_btn = QPushButton("Remove")
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
        self.setWindowTitle("Q1 Introduction JSON Editor")
        self.resize(1100, 800)

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
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        load_btn = QPushButton("Load JSON")
        save_btn = QPushButton("Save JSON")

        load_btn.clicked.connect(self.load_json)
        save_btn.clicked.connect(self.save_json)

        toolbar.addWidget(load_btn)
        toolbar.addWidget(save_btn)

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

    # ---------- Tabs ----------

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
        layout = QHBoxLayout()

        self.ref_list = QListWidget()
        self.ref_list.setEditTriggers(
            QListWidget.DoubleClicked | QListWidget.EditKeyPressed
        )
        self.ref_list.itemChanged.connect(self._on_reference_renamed)
        self.ref_list.currentItemChanged.connect(self._load_reference)

        # ---- Right panel (scrollable) ----
        right_widget = QWidget()
        right = QVBoxLayout()
        right_widget.setLayout(right)

        self.ref_bibtex = LabeledTextEdit("BibTeX", "BibTeX entry. This is the only source for citations.")
        self.ref_abstract = LabeledTextEdit("Abstract", "Original abstract of the cited paper.")
        self.ref_category = LabeledLineEdit("Methodological Category", "e.g., deep_learning, transformer_based, graph_based.")
        self.ref_contribution = LabeledTextEdit("Central Technical Contribution", "Main technical idea introduced by this work.")
        self.ref_strengths = StringListEditor("Author Reported Strengths", "Strengths explicitly claimed by the original authors.")
        self.ref_limitations = StringListEditor("Reported Limitations", "Limitations discussed or implied by the paper.")
        self.ref_relevance = LabeledTextEdit("Relevance to Our Work", "How this work relates to and differs from our paper.")
        self.ref_role = LabeledLineEdit("Introduction Paragraph Role", "foundational, early_state_of_art, recent_advances, etc.")

        for wdg in [
            self.ref_bibtex, self.ref_abstract, self.ref_category,
            self.ref_contribution, self.ref_strengths,
            self.ref_limitations, self.ref_relevance, self.ref_role
        ]:
            right.addWidget(wdg)

        btns = QHBoxLayout()
        add = QPushButton("Add Reference")
        remove = QPushButton("Remove Reference")
        btns.addWidget(add)
        btns.addWidget(remove)

        add.clicked.connect(self._add_reference)
        remove.clicked.connect(self._remove_reference)

        right.addLayout(btns)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(right_widget)

        layout.addWidget(self.ref_list, 1)
        layout.addWidget(scroll, 3)

        w.setLayout(layout)
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
            "central_technical_contribution": self.ref_contribution.get(),
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
        self.ref_contribution.set(ref.get("central_technical_contribution"))
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

        # ---- Related Work: Human Curated Synthesis ----
        synth = data.get("related_work", {}).get("human_curated_synthesis", {})
        self.syn_trends.set(synth.get("common_trends", []))
        self.syn_open.set(synth.get("open_problems", []))
        self.syn_gap.set(synth.get("explicit_research_gap"))
        
        self.current_reference_key = None
        self._clear_reference_editor()

    def save_json(self):
        self._save_current_reference()

        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if not path:
            return

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

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.current_path = path
        self.status.showMessage(f"Saved to {path}")


# ---------- Main ----------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = JsonIntroductionEditor()
    win.show()
    sys.exit(app.exec_())
