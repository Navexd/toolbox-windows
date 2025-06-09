import os
import sys
from functools import partial

from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve
from PySide6.QtGui import QPixmap, QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QDialog, QStackedWidget, QSystemTrayIcon, QMenu
)

from MotV8 import MotDePasseWidget
from config import STYLESHEET_PATH, IMAGES_DIR
from historiqueV8 import HistoriqueWidget
from servicesV8 import ServicesWidget

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Paramètres")
        self.setFixedSize(300, 300)
        self.setStyleSheet("background-color: #2c2c3e; color: #ecf0f1; border-radius: 10px;")

        layout = QVBoxLayout(self)
        btn_example = QPushButton("Exemple de paramètre", self)
        layout.addWidget(btn_example)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    ANIMATION_DURATION = 300
    ANIMATION_CURVE = QEasingCurve.OutCubic

    def __init__(self):
        super().__init__()

        self.setWindowTitle("toolbox-v0.8")
        self.setWindowIcon(QIcon(os.path.join(IMAGES_DIR, "12.svg")))  # Ajout de l'icône
        self.setFixedSize(440, 657)
        self.move(1094, 124)

        self.icons = self.load_icons()

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Barre d'icônes
        icons_layout = QHBoxLayout()
        self.add_icon(icons_layout, "logo", alignment=Qt.AlignLeft)
        self.add_icon(icons_layout, "settings", alignment=Qt.AlignRight, on_click=self.open_settings_window)

        # Contenu principal
        self.content_layout = QStackedWidget()

        # Pages pour chaque section
        self.page1, self.password_generator_widget = self.create_page_with_widget(MotDePasseWidget)
        self.password_generator_widget.password_generated.connect(self.update_password_history)

        self.page2, self.historique_widget = self.create_page_with_widget(HistoriqueWidget)
        self.page3, self.services_widget = self.create_page_with_widget(ServicesWidget)

        self.content_layout.addWidget(self.page1)
        self.content_layout.addWidget(self.page2)
        self.content_layout.addWidget(self.page3)

        # Barre des tâche
        taskbar = self.create_taskbar()

        main_layout.addLayout(icons_layout)
        main_layout.addWidget(taskbar)
        main_layout.addWidget(self.content_layout)
        main_layout.addStretch()

        self.setCentralWidget(central_widget)

        # Sélectionner "Mot de passe" par défaut
        self.highlight_button(0)
        self.change_content(0)

        # Ajout de l'icône au system tray
        self.tray_icon = QSystemTrayIcon(QIcon(os.path.join(IMAGES_DIR, "12.svg")), self)
        self.tray_icon.setToolTip("Toolbox Application")

        # Connecter l'événement double clic
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Créer un menu contextuel pour le system tray
        self.tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)

        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Toolbox Notification",
            "Votre application Toolbox fonctionne en arrière-plan. Pour quitter, utilisez l'option Quitter du menu.",
            QSystemTrayIcon.Information,
            2000
        )

    def load_icons(self):
        return {
            "logo": QPixmap(os.path.join(IMAGES_DIR, "3.png")).scaled(90, 90, Qt.KeepAspectRatio),
            "settings": QPixmap(os.path.join(IMAGES_DIR, "10.png")).scaled(35, 35, Qt.KeepAspectRatio),
        }

    def add_icon(self, layout, icon_key, alignment, on_click=None):
        label = QLabel(self)
        label.setPixmap(self.icons[icon_key])
        layout.addWidget(label, alignment=alignment)
        if on_click:
            label.mousePressEvent = on_click

    def open_settings_window(self, event):
        settings_window = SettingsWindow()
        settings_window.exec()

    def create_page_with_widget(self, widget_class):
        page = QWidget()
        layout = QVBoxLayout(page)
        widget = widget_class()
        layout.addWidget(widget)
        return page, widget

    def create_taskbar(self):
        taskbar = QWidget(self)
        taskbar_layout = QHBoxLayout(taskbar)
        taskbar.setFixedHeight(60)
        taskbar.setObjectName("taskbar")

        self.btn_outils = self.create_taskbar_button("Mot de passe")
        self.btn_projets = self.create_taskbar_button("Historique")
        self.btn_services = self.create_taskbar_button("Services")

        self.reset_button_styles()

        self.btn_outils.clicked.connect(partial(self.change_content, 0))
        self.btn_projets.clicked.connect(partial(self.change_content, 1))
        self.btn_services.clicked.connect(partial(self.change_content, 2))

        taskbar_layout.addWidget(self.btn_outils, alignment=Qt.AlignCenter)
        taskbar_layout.addStretch()
        taskbar_layout.addWidget(self.btn_projets, alignment=Qt.AlignCenter)
        taskbar_layout.addStretch()
        taskbar_layout.addWidget(self.btn_services, alignment=Qt.AlignCenter)

        return taskbar

    def create_taskbar_button(self, text):
        button = QPushButton(text)
        button.setMinimumSize(120, 55)
        return button

    def change_content(self, index):
        current_index = self.content_layout.currentIndex()
        if current_index != index:
            self.animate_transition(current_index, index)
        self.content_layout.setCurrentIndex(index)
        self.highlight_button(index)

    def animate_transition(self, from_index, to_index):
        from_widget = self.content_layout.widget(from_index)
        to_widget = self.content_layout.widget(to_index)

        width = self.content_layout.frameRect().width()

        from_animation = QPropertyAnimation(from_widget, b"geometry")
        from_animation.setDuration(self.ANIMATION_DURATION)
        from_animation.setStartValue(QRect(0, 0, width, from_widget.height()))
        from_animation.setEndValue(QRect(-width, 0, width, from_widget.height()))
        from_animation.setEasingCurve(self.ANIMATION_CURVE)

        to_animation = QPropertyAnimation(to_widget, b"geometry")
        to_animation.setDuration(self.ANIMATION_DURATION)
        to_animation.setStartValue(QRect(width, 0, width, to_widget.height()))
        to_animation.setEndValue(QRect(0, 0, width, to_widget.height()))
        to_animation.setEasingCurve(self.ANIMATION_CURVE)

        animation_group = QParallelAnimationGroup()
        animation_group.addAnimation(from_animation)
        animation_group.addAnimation(to_animation)
        animation_group.start()

    def highlight_button(self, index):
        self.reset_button_styles()

        buttons = [self.btn_outils, self.btn_projets, self.btn_services]
        active_styles = [
            "background-color: #B08F12; color: #C3F8FA; font-size: 16px;",
            "background-color: #968D77; color: #C3F8FA; font-size: 16px;",
            "background-color: #847655; color: #C3F8FA; font-size: 16px;",
        ]

        buttons[index].setStyleSheet(active_styles[index])

    def reset_button_styles(self):
        self.btn_outils.setStyleSheet("background-color: #B08F12; color: #000000; font-size: 16px;")
        self.btn_projets.setStyleSheet("background-color: #968D77; color: #000000; font-size: 16px;")
        self.btn_services.setStyleSheet("background-color: #847655; color: #000000; font-size: 16px;")

    def update_password_history(self, password):
        self.historique_widget.add_password_to_history(password)

def main():
    app = QApplication([])

    if os.path.exists(STYLESHEET_PATH):
        with open(STYLESHEET_PATH, "r") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Stylesheet not found at {STYLESHEET_PATH}")

    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
