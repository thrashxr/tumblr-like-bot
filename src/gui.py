#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import threading
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QGroupBox, 
                            QTextEdit, QProgressBar, QDialog, QLineEdit,
                            QSpinBox, QTimeEdit, QListWidget, QMessageBox,
                            QComboBox, QListWidgetItem, QInputDialog, QCheckBox)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QTime
from loguru import logger
from tumblr_bot import TumblrLikeBot
import time
import yaml
import os
import qtawesome as qta

class LogHandler:
    def __init__(self, callback):
        self.callback = callback

    def write(self, message):
        if message.strip():  # Filter empty messages
            self.callback(message.strip())

    def flush(self):
        pass

class BotWorker(QThread):
    error_occurred = Signal(str)
    status_updated = Signal(dict)
    log_received = Signal(str)
    stopped = Signal()  # New signal

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.is_running = False
        
        # Add log handler
        logger.remove()  # Remove default handlers
        logger.add(LogHandler(self.handle_log), format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}")

    def handle_log(self, message):
        self.log_received.emit(message)

    def run(self):
        self.is_running = True
        try:
            self.bot.run()
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.is_running = False
            self.stopped.emit()

    def stop(self):
        """Stop the bot safely"""
        if self.is_running:
            self.bot.stop_requested = True
            self.is_running = False

class StopWorker(QThread):
    """Thread to manage bot stopping process"""
    finished = Signal()

    def __init__(self, bot_worker):
        super().__init__()
        self.bot_worker = bot_worker

    def run(self):
        try:
            # Stop the bot
            self.bot_worker.stop()
            
            # Wait maximum 5 seconds for the bot to stop
            for _ in range(50):  # 100ms * 50 = 5 seconds
                if not self.bot_worker.isRunning():
                    break
                time.sleep(0.1)
                
            self.finished.emit()
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")
            self.finished.emit()

class CacheUpdateWorker(QThread):
    """Thread to update cache in background"""
    finished = Signal()
    log_received = Signal(str)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    def run(self):
        try:
            self.bot.update_liked_posts_cache()
        finally:
            self.finished.emit()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        # Define icons as class properties
        self.plus_icon = qta.icon('fa5s.plus', color='white')
        self.minus_icon = qta.icon('fa5s.minus', color='white')
        self.save_icon = qta.icon('fa5s.save', color='white')
        self.times_icon = qta.icon('fa5s.times', color='white')
        
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
        self.load_config()
        
        # Dark theme styles
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                background-color: #333333;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                color: #00ff00;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel {
                color: #e1e1e1;
                padding: 5px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #1565c0;
            }
            QComboBox:focus {
                border-color: #1976d2;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #0d47a1;
                width: 25px;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                selection-background-color: #0d47a1;
                selection-color: #ffffff;
                border: 2px solid #3d3d3d;
            }
            QSpinBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }
            QSpinBox:hover {
                border-color: #1565c0;
            }
            QSpinBox:focus {
                border-color: #1976d2;
            }
            QTimeEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }
            QTimeEdit:hover {
                border-color: #1565c0;
            }
            QTimeEdit:focus {
                border-color: #1976d2;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 2px;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
            QListWidget::item:selected {
                background-color: #0d47a1;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3d3d3d;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:hover {
                border-color: #1565c0;
            }
            QCheckBox::indicator:checked {
                background-color: #0d47a1;
                border-color: #0d47a1;
                image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNCIgaGVpZ2h0PSIxNCIgdmlld0JveD0iMCAwIDE0IDE0Ij48cGF0aCBmaWxsPSIjZmZmZmZmIiBkPSJNMTEuNDIgMi4yNUw0LjgxNyA4Ljg1IDIuNTggNi42MTYgMS40IDcuOGwzLjQxNyAzLjQxNyA3Ljc4My03Ljc4My0xLjE4LTEuMTg0eiIvPjwvc3ZnPg==");
            }
        """)
        
        self.init_ui()

    def load_config(self):
        """Load configuration file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration file: {str(e)}")
            self.config = {}

    def save_config(self):
        """Save configuration file"""
        try:
            # Transfer values to config dictionary
            self.config['like_settings']['max_likes_per_hour'] = self.max_likes_hour_spin.value()
            self.config['like_settings']['max_likes_per_day'] = self.max_likes_day_spin.value()
            self.config['like_settings']['min_notes'] = self.min_notes_spin.value()
            
            # Get tags
            tags = []
            for i in range(self.tags_list.count()):
                tags.append(self.tags_list.item(i).text())
            self.config['like_settings']['tags'] = tags
            
            # Get content types
            content_types = []
            for i in range(self.content_types_list.count()):
                if self.content_types_list.item(i).checkState() == Qt.Checked:
                    content_types.append(self.content_types_list.item(i).text())
            self.config['like_settings']['content_types'] = content_types
            
            # Timing settings
            self.config['timing']['delay_between_likes'] = self.delay_spin.value()
            self.config['timing']['rest_time'] = self.rest_time_spin.value()
            self.config['timing']['enable_work_hours'] = self.enable_work_hours.isChecked()
            self.config['timing']['start_time'] = self.start_time.time().toString('HH:mm')
            self.config['timing']['end_time'] = self.end_time.time().toString('HH:mm')
            
            # Log settings
            self.config['logging']['level'] = self.log_level_combo.currentText()
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True)
            
            QMessageBox.information(self, "Success", "Settings saved!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Like Settings
        like_group = QGroupBox("Like Settings")
        like_layout = QVBoxLayout()
        
        # Hourly and daily limits
        limits_layout = QHBoxLayout()
        self.max_likes_hour_spin = QSpinBox()
        self.max_likes_hour_spin.setRange(1, 1000)
        self.max_likes_hour_spin.setValue(self.config['like_settings']['max_likes_per_hour'])
        self.max_likes_hour_spin.setFixedWidth(100)
        self.max_likes_hour_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        limits_layout.addWidget(QLabel("Hourly Limit:"))
        limits_layout.addWidget(self.max_likes_hour_spin)
        
        self.max_likes_day_spin = QSpinBox()
        self.max_likes_day_spin.setRange(1, 5000)
        self.max_likes_day_spin.setValue(self.config['like_settings']['max_likes_per_day'])
        self.max_likes_day_spin.setFixedWidth(100)
        self.max_likes_day_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        limits_layout.addWidget(QLabel("Daily Limit:"))
        limits_layout.addWidget(self.max_likes_day_spin)
        
        like_layout.addLayout(limits_layout)
        
        # Minimum notes count
        notes_layout = QHBoxLayout()
        self.min_notes_spin = QSpinBox()
        self.min_notes_spin.setRange(0, 1000)
        self.min_notes_spin.setValue(self.config['like_settings']['min_notes'])
        self.min_notes_spin.setFixedWidth(100)
        self.min_notes_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        notes_layout.addWidget(QLabel("Minimum Notes Count:"))
        notes_layout.addWidget(self.min_notes_spin)
        like_layout.addLayout(notes_layout)
        
        # Tags
        tags_layout = QVBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_list = QListWidget()
        self.tags_list.addItems(self.config['like_settings']['tags'])
        tags_layout.addWidget(self.tags_list)
        
        # Tag buttons
        tag_buttons_layout = QHBoxLayout()
        add_tag_button = QPushButton("Add Tag")
        add_tag_button.setIcon(self.plus_icon)
        remove_tag_button = QPushButton("Remove Tag")
        remove_tag_button.setIcon(self.minus_icon)
        add_tag_button.clicked.connect(self.add_tag)
        remove_tag_button.clicked.connect(self.remove_tag)
        tag_buttons_layout.addWidget(add_tag_button)
        tag_buttons_layout.addWidget(remove_tag_button)
        tags_layout.addLayout(tag_buttons_layout)
        like_layout.addLayout(tags_layout)
        
        # Content types
        content_layout = QVBoxLayout()
        content_layout.addWidget(QLabel("Content Types:"))
        self.content_types_list = QListWidget()
        all_content_types = ['text', 'photo', 'quote', 'link', 'chat', 'audio', 'video', 'answer']
        for content_type in all_content_types:
            item = QListWidgetItem(content_type)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if content_type in self.config['like_settings']['content_types'] else Qt.Unchecked)
            self.content_types_list.addItem(item)
        content_layout.addWidget(self.content_types_list)
        like_layout.addLayout(content_layout)
        
        like_group.setLayout(like_layout)
        layout.addWidget(like_group)
        
        # Timing Settings
        timing_group = QGroupBox("Timing Settings")
        timing_layout = QVBoxLayout()
        
        # Delay settings
        delay_layout = QHBoxLayout()
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 3600)
        self.delay_spin.setValue(self.config['timing']['delay_between_likes'])
        self.delay_spin.setFixedWidth(100)
        self.delay_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        delay_layout.addWidget(QLabel("Delay Between Likes (sec):"))
        delay_layout.addWidget(self.delay_spin)
        
        self.rest_time_spin = QSpinBox()
        self.rest_time_spin.setRange(1, 86400)
        self.rest_time_spin.setValue(self.config['timing']['rest_time'])
        self.rest_time_spin.setFixedWidth(100)
        self.rest_time_spin.setButtonSymbols(QSpinBox.UpDownArrows)
        delay_layout.addWidget(QLabel("Rest Time (sec):"))
        delay_layout.addWidget(self.rest_time_spin)
        timing_layout.addLayout(delay_layout)
        
        # Working hours
        hours_layout = QHBoxLayout()
        
        # Working hours control checkbox
        self.enable_work_hours = QCheckBox("Enable Working Hours")
        self.enable_work_hours.setChecked(self.config['timing'].get('enable_work_hours', True))
        self.enable_work_hours.stateChanged.connect(self.toggle_work_hours)
        timing_layout.addWidget(self.enable_work_hours)
        
        self.start_time = QTimeEdit()
        self.start_time.setFixedWidth(100)
        self.start_time.setButtonSymbols(QTimeEdit.UpDownArrows)
        self.end_time = QTimeEdit()
        self.end_time.setFixedWidth(100)
        self.end_time.setButtonSymbols(QTimeEdit.UpDownArrows)
        self.start_time.setTime(QTime.fromString(self.config['timing']['start_time'], 'HH:mm'))
        self.end_time.setTime(QTime.fromString(self.config['timing']['end_time'], 'HH:mm'))
        
        hours_layout.addWidget(QLabel("Start Time:"))
        hours_layout.addWidget(self.start_time)
        hours_layout.addWidget(QLabel("End Time:"))
        hours_layout.addWidget(self.end_time)
        timing_layout.addLayout(hours_layout)
        
        # Set time controls based on initial state
        self.toggle_work_hours(self.enable_work_hours.checkState())
        
        timing_group.setLayout(timing_layout)
        layout.addWidget(timing_group)
        
        # Log Settings
        log_group = QGroupBox("Log Settings")
        log_layout = QHBoxLayout()
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.log_level_combo.setCurrentText(self.config['logging']['level'])
        log_layout.addWidget(QLabel("Log Level:"))
        log_layout.addWidget(self.log_level_combo)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Save and Cancel buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.setIcon(self.save_icon)
        cancel_button = QPushButton("Cancel")
        cancel_button.setIcon(self.times_icon)
        save_button.clicked.connect(self.save_config)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def add_tag(self):
        """Add new tag"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add Tag")
        dialog.setLabelText("Tag:")
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #e1e1e1;
                padding: 5px;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
        """)
        
        if dialog.exec() == QDialog.Accepted:
            tag = dialog.textValue()
            if tag:
                self.tags_list.addItem(tag)

    def remove_tag(self):
        """Remove selected tag"""
        current_item = self.tags_list.currentItem()
        if current_item:
            self.tags_list.takeItem(self.tags_list.row(current_item))

    def toggle_work_hours(self, state):
        """Enable/disable working hours"""
        enabled = state == Qt.Checked
        self.start_time.setEnabled(enabled)
        self.end_time.setEnabled(enabled)

class TumblrBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Define icons
        play_icon = qta.icon('fa5s.play', color='white')
        stop_icon = qta.icon('fa5s.stop', color='white')
        trash_icon = qta.icon('fa5s.trash-alt', color='white')
        cog_icon = qta.icon('fa5s.cog', color='white')
        plus_icon = qta.icon('fa5s.plus', color='white')
        minus_icon = qta.icon('fa5s.minus', color='white')
        
        self.bot = TumblrLikeBot(auto_update_cache=False)
        self.bot_worker = None
        self.stop_worker = None
        self.cache_worker = None
        self.start_time = None
        self.init_ui()
        self.start_update_timer()
        
        # Start cache update in background
        self.start_cache_update()

    def init_ui(self):
        """Initialize user interface"""
        # Define icons
        play_icon = qta.icon('fa5s.play', color='white')
        stop_icon = qta.icon('fa5s.stop', color='white')
        trash_icon = qta.icon('fa5s.trash-alt', color='white')
        cog_icon = qta.icon('fa5s.cog', color='white')
        plus_icon = qta.icon('fa5s.plus', color='white')
        minus_icon = qta.icon('fa5s.minus', color='white')
        
        self.setWindowTitle('Tumblr Auto Like Bot')
        self.setMinimumSize(800, 600)
        
        # Main theme and styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                color: #ffffff;
                font-size: 10pt;
            }
            QGroupBox {
                background-color: #333333;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #00ff00;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLabel {
                color: #e1e1e1;
                padding: 5px;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QPushButton:disabled {
                background-color: #666666;
            }
            QProgressBar {
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #1e88e5;
                border-radius: 3px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: Consolas, Monaco, monospace;
                font-size: 10pt;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Content area container
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setSpacing(10)

        # Layout for Status, Statistics and Log groups
        groups_layout = QVBoxLayout()
        
        # Place Status and Statistics groups side by side
        top_groups = QHBoxLayout()
        
        # Status Group
        status_group = QGroupBox("Bot Status")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        # Status labels
        self.status_label = QLabel("Status: Waiting")
        self.runtime_label = QLabel("Runtime: 00:00:00")
        self.current_tag_label = QLabel("Current Tag: -")
        
        # Special style for labels
        for label in [self.status_label, self.runtime_label, self.current_tag_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: #2b2b2b;
                    border-radius: 3px;
                    padding: 8px;
                }
            """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.runtime_label)
        status_layout.addWidget(self.current_tag_label)
        status_group.setLayout(status_layout)
        
        # Statistics Group
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        
        # Statistics labels
        self.total_likes_label = QLabel("Total Likes: 0")
        self.hourly_likes_label = QLabel("Hourly Likes: 0")
        self.daily_likes_label = QLabel("Daily Likes: 0")
        self.error_count_label = QLabel("Error Count: 0")
        self.last_like_label = QLabel("Last Like: -")
        self.skipped_posts_label = QLabel("Skipped Posts: 0")
        
        # Special style for statistics labels
        for label in [self.total_likes_label, self.hourly_likes_label, 
                     self.daily_likes_label, self.error_count_label, 
                     self.last_like_label, self.skipped_posts_label]:
            label.setStyleSheet("""
                QLabel {
                    background-color: #2b2b2b;
                    border-radius: 3px;
                    padding: 8px;
                }
            """)
        
        stats_layout.addWidget(self.total_likes_label)
        stats_layout.addWidget(self.hourly_likes_label)
        stats_layout.addWidget(self.daily_likes_label)
        stats_layout.addWidget(self.error_count_label)
        stats_layout.addWidget(self.last_like_label)
        stats_layout.addWidget(self.skipped_posts_label)
        stats_group.setLayout(stats_layout)
        
        # Add Status and Statistics groups side by side
        top_groups.addWidget(status_group)
        top_groups.addWidget(stats_group)
        
        # Add groups to main layout
        groups_layout.addLayout(top_groups)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        log_layout.setSpacing(5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        groups_layout.addWidget(log_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% Completed")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                height: 25px;
                text-align: center;
                color: black;
                font-weight: bold;
            }
        """)
        groups_layout.addWidget(self.progress_bar)
        
        # Add groups to content container
        content_layout.addLayout(groups_layout)
        
        # Add content container to main layout
        layout.addWidget(content_container, stretch=1)
        
        # Bottom panel for all buttons
        button_panel = QWidget()
        button_panel.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-top: 2px solid #3d3d3d;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_panel)
        button_layout.setSpacing(10)
        
        # Left side buttons
        left_buttons = QHBoxLayout()
        clear_log_button = QPushButton("Clear Logs")
        clear_log_button.setIcon(trash_icon)
        clear_log_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
            }
            QPushButton:hover {
                background-color: #ef5350;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        clear_log_button.clicked.connect(self.clear_logs)
        left_buttons.addWidget(clear_log_button)
        
        # Settings button
        settings_button = QPushButton("Settings")
        settings_button.setIcon(cog_icon)
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1e88e5;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        settings_button.clicked.connect(self.show_settings)
        left_buttons.addWidget(settings_button)
        
        # Right side buttons
        right_buttons = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.setIcon(play_icon)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setIcon(stop_icon)
        self.stop_button.setEnabled(False)
        
        # Special style for Start button
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;  /* Dark green */
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #388e3c;  /* Medium green */
            }
            QPushButton:pressed {
                background-color: #1b5e20;  /* Darker green */
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        
        # Special style for Stop button
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;  /* Dark red */
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ef5350;  /* Medium red */
            }
            QPushButton:pressed {
                background-color: #c62828;  /* Darker red */
            }
            QPushButton:disabled {
                background-color: #666666;
            }
        """)
        
        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)
        
        right_buttons.addWidget(self.start_button)
        right_buttons.addWidget(self.stop_button)
        
        # Add buttons to panel layout
        button_layout.addLayout(left_buttons)
        button_layout.addStretch()
        button_layout.addLayout(right_buttons)
        
        # Add button panel to main layout
        layout.addWidget(button_panel)

    def clear_logs(self):
        """Clear log area"""
        self.log_text.clear()

    def start_update_timer(self):
        """Start periodic update timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second

    def update_stats(self):
        """Update statistics"""
        if hasattr(self.bot, 'stats'):
            # Update runtime
            if self.start_time and self.bot_worker and self.bot_worker.is_running:
                elapsed_time = datetime.now() - self.start_time
                hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.runtime_label.setText(f"Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            self.total_likes_label.setText(f"Total Likes: {self.bot.stats['total_likes']}")
            self.hourly_likes_label.setText(f"Hourly Likes: {self.bot.like_count['hour']}")
            self.daily_likes_label.setText(f"Daily Likes: {self.bot.like_count['day']}")
            self.error_count_label.setText(f"Error Count: {self.bot.stats['errors']}")
            self.skipped_posts_label.setText(f"Skipped Posts: {self.bot.stats['skipped_posts']}")
            
            if self.bot.stats['last_like']:
                self.last_like_label.setText(f"Last Like: {self.bot.stats['last_like'].strftime('%H:%M:%S')}")
            
            if self.bot.stats['current_tag']:
                self.current_tag_label.setText(f"Current Tag: {self.bot.stats['current_tag']}")

            # Update progress bar
            if self.bot_worker and self.bot_worker.is_running:
                self.progress_bar.setValue((self.bot.like_count['hour'] / self.bot.config['like_settings']['max_likes_per_hour']) * 100)

    def add_log(self, message):
        """Add log message"""
        # Determine color based on log level
        color = "#ffffff"  # default white
        if "DEBUG" in message:
            color = "#808080"  # gray
        elif "INFO" in message:
            color = "#00ff00"  # green
        elif "WARNING" in message:
            color = "#ffa500"  # orange
        elif "ERROR" in message:
            color = "#ff0000"  # red
        
        # Create HTML formatted colored message
        formatted_message = f'<span style="color: {color}">{message}</span>'
        
        # Add message and scroll to bottom
        self.log_text.append(formatted_message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def start_bot(self):
        """Start the bot"""
        if not self.bot_worker or not self.bot_worker.is_running:
            self.start_time = datetime.now()  # Record start time
            self.bot_worker = BotWorker(self.bot)
            self.bot_worker.error_occurred.connect(self.handle_error)
            self.bot_worker.log_received.connect(self.add_log)
            self.bot_worker.stopped.connect(self.handle_bot_stopped)
            self.bot_worker.start()
            
            self.status_label.setText("Status: Running")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.add_log("Bot started")

    def stop_bot(self):
        """Stop the bot"""
        if self.bot_worker and self.bot_worker.is_running:
            self.status_label.setText("Status: Stopping...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.add_log("Stopping bot...")
            
            # Stop the bot in a separate thread
            self.stop_worker = StopWorker(self.bot_worker)
            self.stop_worker.finished.connect(self.handle_bot_stopped)
            self.stop_worker.start()

    def handle_bot_stopped(self):
        """Called when bot is stopped"""
        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.add_log("Bot stopped")
        self.start_time = None  # Reset runtime
        self.runtime_label.setText("Runtime: 00:00:00")
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Cleanup workers
        if self.bot_worker:
            self.bot_worker.deleteLater()
            self.bot_worker = None
            
        if self.stop_worker:
            self.stop_worker.deleteLater()
            self.stop_worker = None

    def handle_error(self, error_message):
        """Handle error messages"""
        self.add_log(f"ERROR: {error_message}")
        self.status_label.setText("Status: Error!")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def closeEvent(self, event):
        """Stop bot and cleanup when program is closed"""
        try:
            # Stop the update timer
            if hasattr(self, 'update_timer'):
                self.update_timer.stop()
            
            # Stop the bot if running
            if self.bot_worker and self.bot_worker.is_running:
                self.stop_bot()
                
                # Wait maximum 5 seconds for bot to stop
                for _ in range(50):  # 100ms * 50 = 5 seconds
                    if not self.bot_worker.isRunning():
                        break
                    QApplication.processEvents()  # Keep UI responsive
                    time.sleep(0.1)
                    
            # Wait for cache worker to finish
            if self.cache_worker and self.cache_worker.isRunning():
                self.cache_worker.wait()
                
            # Cleanup workers
            if self.bot_worker:
                self.bot_worker.wait()  # Wait for thread to finish
                self.bot_worker.deleteLater()
                
            if self.stop_worker:
                self.stop_worker.wait()  # Wait for thread to finish
                self.stop_worker.deleteLater()
                
            if self.cache_worker:
                self.cache_worker.deleteLater()
                
            event.accept()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            event.accept()

    def show_settings(self):
        """Show settings dialog"""
        if self.bot_worker and self.bot_worker.is_running:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warning")
            msg.setText("Please stop the bot before changing settings!")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMessageBox QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0a3d91;
                }
            """)
            msg.exec()
            return
            
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.bot = TumblrLikeBot()
            self.add_log("Settings updated, restarting bot...")

    def start_cache_update(self):
        """Start cache update in background"""
        if not self.cache_worker:
            self.cache_worker = CacheUpdateWorker(self.bot)
            self.cache_worker.finished.connect(self.handle_cache_update_finished)
            self.cache_worker.start()
            self.add_log("Updating cache...")

    def handle_cache_update_finished(self):
        """Called when cache update is completed"""
        self.add_log("Cache update completed")
        if self.cache_worker:
            self.cache_worker.deleteLater()
            self.cache_worker = None

def main():
    app = QApplication(sys.argv)
    window = TumblrBotGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 