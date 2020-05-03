#!/usr/local/bin/python3
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QTableWidget, QLabel, QMessageBox, QTableWidgetItem, QAbstractItemView, QCompleter
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from pypinyin import lazy_pinyin, Style


class InputBox:
    def __init__(self, info: str, func=QLineEdit):
        self.layout = QHBoxLayout()
        self.line_edit = func()
        self.layout.addWidget(QLabel(info))
        self.layout.addWidget(self.line_edit)


class InfoBox:
    def __init__(self, info: str):
        self.layout = QHBoxLayout()
        self.label = QLabel()
        self.layout.addWidget(QLabel(info))
        self.layout.addWidget(self.label)

    def set(self, info):
        self.label.setText(info)


app = QApplication([])
main_window = QWidget()


def createTable():
    table = QTableWidget(0, 5)
    table.setHorizontalHeaderLabels(['药品名称', '单价', '日份数', '总份数', '价格'])
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    return table


table_widget = createTable()

tot_price = 0
price_info = InfoBox('总价格：')
aging = 0
aging_info = InfoBox('天数：')


def newPrescription():
    aging_widget = QWidget()
    layout = QVBoxLayout()
    aging_widget.setLayout(layout)

    pre_aging = InputBox('药方天数:')
    pre_aging.line_edit.setValidator(QIntValidator())
    layout.addLayout(pre_aging.layout)

    submit = QPushButton('确定')
    layout.addWidget(submit)

    def submit_onclick():
        global aging, tot_price
        if (pre_aging.line_edit.text() == ''):
            QMessageBox(text="输入为空").exec_()
            return
        aging = int(pre_aging.line_edit.text())
        if (aging < 1):
            QMessageBox(text="天数至少为一天").exec_()
            return
        aging_widget.close()
        aging_info.set(str(aging))
        tot_price = 0
        price_info.set(str(tot_price))
        table_widget.setRowCount(0)
        main_window.show()

    submit.clicked.connect(submit_onclick)

    main_window.hide()
    aging_widget.show()


data = {}


def float2str(x: float):
    return "%.2f" % (x)


model = QStandardItemModel()


def inp_layout():
    proxy = QSortFilterProxyModel()
    proxy.setSourceModel(model)
    proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
    proxy.setFilterKeyColumn(-1)
    inp_layout = QHBoxLayout()
    med_name = InputBox('药品名称:')
    inp_layout.addLayout(med_name.layout)
    completer = QCompleter()
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setModel(proxy)
    completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
    med_name.line_edit.setCompleter(completer)

    def func(x):
        proxy.setFilterFixedString(x)
        for i in range(completer.completionModel().rowCount()):
            completer.setCurrentRow(i)
        return

    med_name.line_edit.textEdited.connect(func)
    med_weight = InputBox('克数:')
    med_weight.line_edit.setValidator(QDoubleValidator())
    inp_layout.addLayout(med_weight.layout)
    button = QPushButton('添加')
    inp_layout.addWidget(button)

    def onclick():
        name = med_name.line_edit.text()
        weight = med_weight.line_edit.text()
        if name == '' or weight == '':
            QMessageBox(text="名字和重量不能为空").exec_()
            return
        weight = float(weight)
        if weight <= 0:
            QMessageBox(text="重量要为正数").exec_()
            return

        if data.get(name) is None:
            QMessageBox(text="找不到此药品").exec_()
            return

        new_row = table_widget.rowCount()
        table_widget.insertRow(new_row)
        table_widget.setItem(new_row, 0, QTableWidgetItem(name))
        table_widget.setItem(new_row, 1, QTableWidgetItem(float2str(data[name].price)))
        cnt = round(max(1, weight/data[name].weight))
        table_widget.setItem(new_row, 2, QTableWidgetItem(str(cnt)))
        table_widget.setItem(new_row, 3, QTableWidgetItem(str(cnt * aging)))
        table_widget.setItem(new_row, 4, QTableWidgetItem(float2str(cnt * aging * data[name].price)))
        # table_widget.setRowCount(5)
        global tot_price
        tot_price += cnt * aging * data[name].price
        price_info.set(float2str(tot_price))
        main_window.update()

        med_name.line_edit.setText('')
        med_weight.line_edit.setText('')
        return
    button.clicked.connect(onclick)
    return inp_layout


data_path = 'data.csv'


class Medician:
    def __init__(self, item):
        self.name = item[0]
        self.price = round(float(item[2]) * 1.15, 3)
        self.weight = float(item[1])


def read_database():
    import csv
    with open("data.csv", "r") as csvFile:
        reader = csv.reader(csvFile)
        global data
        data = {}
        for item in reader:
            # 忽略第一行
            if reader.line_num == 1:
                continue
            data[item[0]] = Medician(item)
            name = QStandardItem(item[0])
            py = QStandardItem(''.join(lazy_pinyin(item[0], style=Style.FIRST_LETTER)))
            pinyin = QStandardItem(''.join(lazy_pinyin(item[0])))
            model.appendRow([name, py, pinyin])



def init():
    read_database()


if __name__ == '__main__':
    init()
    layout = QVBoxLayout()
    layout.addWidget(table_widget)
    info_layout = QHBoxLayout()
    info_layout.addLayout(price_info.layout)
    info_layout.addLayout(aging_info.layout)
    layout.addLayout(info_layout)
    layout.addLayout(inp_layout())
    button = QPushButton('清除')

    def onclick():
        newPrescription()
        return

    button.clicked.connect(onclick)
    layout.addWidget(button)
    main_window.setLayout(layout)
    newPrescription()
    app.exec_()
# vim: ts=4 sw=4 sts=4 expandtab
