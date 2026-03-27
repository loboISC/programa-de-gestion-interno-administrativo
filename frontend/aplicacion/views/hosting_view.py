from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


@dataclass
class DomainEntry:
    domain_name: str
    domain_url: str
    expiration_date: str
    last_payment_date: str


@dataclass
class MailboxEntry:
    email_address: str
    password: str
    owner_name: str


@dataclass
class HostingProviderData:
    id: str | None
    provider_name: str
    access_url: str
    account_username: str
    account_password: str
    domains: list[DomainEntry] = field(default_factory=list)
    mailboxes: list[MailboxEntry] = field(default_factory=list)


class HostingProviderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar proveedor de hosting")
        self.setMinimumWidth(920)

        root = QVBoxLayout(self)
        root.setSpacing(16)

        provider_group = QGroupBox("Datos del proveedor")
        provider_layout = QFormLayout(provider_group)

        self.provider_name_input = QLineEdit()
        self.provider_name_input.setPlaceholderText("Ej. Hostinger, DigitalOcean, AWS")
        self.access_url_input = QLineEdit()
        self.access_url_input.setPlaceholderText("https://...")
        self.account_username_input = QLineEdit()
        self.account_username_input.setPlaceholderText("Usuario de acceso")
        self.account_password_input = QLineEdit()
        self.account_password_input.setPlaceholderText("Contraseña de la cuenta")
        self.account_password_input.setEchoMode(QLineEdit.Password)

        provider_layout.addRow("Proveedor", self.provider_name_input)
        provider_layout.addRow("URL del login", self.access_url_input)
        provider_layout.addRow("Usuario", self.account_username_input)
        provider_layout.addRow("Contraseña", self.account_password_input)

        domains_group = QGroupBox("Dominios")
        domains_layout = QVBoxLayout(domains_group)
        domains_helper = QLabel("Registra dominio, vencimiento, último pago y URL.")
        domains_helper.setObjectName("MutedText")
        self.domains_table = QTableWidget(0, 4)
        self.domains_table.setHorizontalHeaderLabels(["Dominio", "Vencimiento", "Ultimo pago", "URL"])
        self.domains_table.horizontalHeader().setStretchLastSection(True)
        add_domain_button = QPushButton("Agregar dominio")
        add_domain_button.clicked.connect(self.add_domain_row)
        domains_layout.addWidget(domains_helper)
        domains_layout.addWidget(self.domains_table)
        domains_layout.addWidget(add_domain_button, alignment=Qt.AlignLeft)

        mailboxes_group = QGroupBox("Buzones de correo")
        mailboxes_layout = QVBoxLayout(mailboxes_group)
        mailboxes_helper = QLabel("Registra correo, contraseña y responsable.")
        mailboxes_helper.setObjectName("MutedText")
        self.mailboxes_table = QTableWidget(0, 3)
        self.mailboxes_table.setHorizontalHeaderLabels(["Correo", "Contraseña", "Pertenece a"])
        self.mailboxes_table.horizontalHeader().setStretchLastSection(True)
        add_mailbox_button = QPushButton("Agregar buzón")
        add_mailbox_button.clicked.connect(self.add_mailbox_row)
        mailboxes_layout.addWidget(mailboxes_helper)
        mailboxes_layout.addWidget(self.mailboxes_table)
        mailboxes_layout.addWidget(add_mailbox_button, alignment=Qt.AlignLeft)

        self.status_label = QLabel("Completa los datos base y agrega los dominios o buzones que necesites.")
        self.status_label.setObjectName("MutedText")
        self.status_label.setWordWrap(True)

        buttons = QHBoxLayout()
        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)
        save_button = QPushButton("Guardar proveedor")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self._validate_and_accept)
        buttons.addStretch(1)
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        root.addWidget(provider_group)
        root.addWidget(domains_group)
        root.addWidget(mailboxes_group)
        root.addWidget(self.status_label)
        root.addLayout(buttons)

        self.add_domain_row()
        self.add_mailbox_row()

    def add_domain_row(self):
        row = self.domains_table.rowCount()
        self.domains_table.insertRow(row)
        for column in range(4):
            self.domains_table.setItem(row, column, QTableWidgetItem(""))

    def add_mailbox_row(self):
        row = self.mailboxes_table.rowCount()
        self.mailboxes_table.insertRow(row)
        for column in range(3):
            self.mailboxes_table.setItem(row, column, QTableWidgetItem(""))

    def _validate_and_accept(self):
        if not all(
            [
                self.provider_name_input.text().strip(),
                self.access_url_input.text().strip(),
                self.account_username_input.text().strip(),
                self.account_password_input.text(),
            ]
        ):
            self.status_label.setStyleSheet("color: #b24d3e;")
            self.status_label.setText("Proveedor, URL, usuario y contraseña son obligatorios.")
            return
        self.accept()

    def _table_value(self, table: QTableWidget, row: int, column: int) -> str:
        item = table.item(row, column)
        return item.text().strip() if item else ""

    def get_payload(self) -> dict:
        domains = []
        for row in range(self.domains_table.rowCount()):
            domain_name = self._table_value(self.domains_table, row, 0)
            if not domain_name:
                continue
            domains.append(
                {
                    "domain_name": domain_name,
                    "expiration_date": self._table_value(self.domains_table, row, 1),
                    "last_payment_date": self._table_value(self.domains_table, row, 2),
                    "domain_url": self._table_value(self.domains_table, row, 3),
                }
            )

        mailboxes = []
        for row in range(self.mailboxes_table.rowCount()):
            email_address = self._table_value(self.mailboxes_table, row, 0)
            if not email_address:
                continue
            mailboxes.append(
                {
                    "email_address": email_address,
                    "password": self._table_value(self.mailboxes_table, row, 1),
                    "owner_name": self._table_value(self.mailboxes_table, row, 2),
                }
            )

        return {
            "provider_name": self.provider_name_input.text().strip(),
            "access_url": self.access_url_input.text().strip(),
            "account_username": self.account_username_input.text().strip(),
            "account_password": self.account_password_input.text(),
            "domains": domains,
            "mailboxes": mailboxes,
        }


class HostingProvidersView(QFrame):
    def __init__(self, api_client=None, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentPanel")
        self.api_client = api_client
        self.providers: list[dict] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Proveedores de Hosting")
        title.setObjectName("SectionTitle")
        subtitle = QLabel("Control centralizado de accesos, dominios, pagos y buzones.")
        subtitle.setObjectName("MutedText")

        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar proveedor, URL o usuario...")
        self.search_input.textChanged.connect(self.load_providers)

        add_button = QPushButton("Agregar proveedor")
        add_button.setObjectName("PrimaryButton")
        add_button.clicked.connect(self.open_add_dialog)

        top_bar.addWidget(self.search_input, 1)
        top_bar.addWidget(add_button)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.addStretch(1)
        self.scroll.setWidget(self.cards_container)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(top_bar)
        layout.addWidget(self.scroll)

    def load_providers(self) -> None:
        if not self.api_client:
            return
        try:
            self.providers = self.api_client.list_hosting_providers(self.search_input.text().strip())
            self.render_cards()
        except Exception as exc:
            self._show_warning(f"No se pudieron cargar los proveedores: {exc}")

    def render_cards(self) -> None:
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.providers:
            empty = QFrame()
            empty.setObjectName("SurfaceCard")
            empty_layout = QVBoxLayout(empty)
            empty_layout.setContentsMargins(20, 20, 20, 20)
            empty_layout.addWidget(QLabel("Todavía no hay proveedores registrados para este usuario."))
            self.cards_layout.addWidget(empty)
            self.cards_layout.addStretch(1)
            return

        for provider in self.providers:
            self.cards_layout.addWidget(self._build_provider_card(provider))
        self.cards_layout.addStretch(1)

    def _build_provider_card(self, provider: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("SurfaceCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        top = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel(provider["provider_name"])
        title.setObjectName("SectionTitle")
        meta = QLabel(f"Usuario: {provider['account_username']}  |  Login: {provider['access_url']}")
        meta.setObjectName("MutedText")
        title_block.addWidget(title)
        title_block.addWidget(meta)

        buttons = QHBoxLayout()
        open_button = QPushButton("Abrir login")
        open_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(provider["access_url"])))
        delete_button = QPushButton("Eliminar")
        delete_button.setObjectName("DangerButton")
        delete_button.clicked.connect(lambda: self.delete_provider(provider["id"], provider["provider_name"]))
        buttons.addWidget(open_button)
        buttons.addWidget(delete_button)

        top.addLayout(title_block, 1)
        top.addLayout(buttons)

        credentials = QLabel(
            f"Acceso principal: {provider['account_username']} | Contraseña: {self._mask(provider.get('account_password', ''))}"
        )
        credentials.setObjectName("MutedText")

        domains_group = self._build_table_group(
            "Dominios",
            ["Dominio", "Vencimiento", "Ultimo pago", "URL"],
            [
                [
                    domain.get("domain_name", ""),
                    domain.get("expiration_date", ""),
                    domain.get("last_payment_date", ""),
                    domain.get("domain_url", ""),
                ]
                for domain in provider.get("domains", [])
            ],
            "No hay dominios registrados.",
        )

        mailboxes_group = self._build_table_group(
            "Buzones",
            ["Correo", "Contraseña", "Pertenece a"],
            [
                [
                    mailbox.get("email_address", ""),
                    self._mask(mailbox.get("password", "")),
                    mailbox.get("owner_name", ""),
                ]
                for mailbox in provider.get("mailboxes", [])
            ],
            "No hay buzones registrados.",
        )

        layout.addLayout(top)
        layout.addWidget(credentials)
        layout.addWidget(domains_group)
        layout.addWidget(mailboxes_group)
        return card

    def _build_table_group(self, title: str, headers: list[str], rows: list[list[str]], empty_message: str) -> QFrame:
        group = QFrame()
        inner = QVBoxLayout(group)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(8)

        label = QLabel(title)
        label.setStyleSheet("font-weight: 700; font-size: 15px;")
        inner.addWidget(label)

        if not rows:
            empty = QLabel(empty_message)
            empty.setObjectName("MutedText")
            inner.addWidget(empty)
            return group

        table = QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)

        for row_index, row_data in enumerate(rows):
            for column_index, value in enumerate(row_data):
                table.setItem(row_index, column_index, QTableWidgetItem(value))

        table.resizeColumnsToContents()
        inner.addWidget(table)
        return group

    def open_add_dialog(self) -> None:
        dialog = HostingProviderDialog(self)
        if dialog.exec():
            payload = dialog.get_payload()
            try:
                self.api_client.create_hosting_provider(payload)
                self.load_providers()
            except Exception as exc:
                self._show_warning(f"No se pudo guardar el proveedor: {exc}")

    def delete_provider(self, provider_id: str, provider_name: str) -> None:
        answer = QMessageBox.question(
            self,
            "Eliminar proveedor",
            f"¿Eliminar el proveedor {provider_name} y toda su información asociada?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            self.api_client.delete_hosting_provider(provider_id)
            self.load_providers()
        except Exception as exc:
            self._show_warning(f"No se pudo eliminar el proveedor: {exc}")

    def _mask(self, value: str) -> str:
        if not value:
            return ""
        return "•" * min(max(len(value), 8), 14)

    def _show_warning(self, message: str) -> None:
        QMessageBox.warning(self, "Hosting", message)
