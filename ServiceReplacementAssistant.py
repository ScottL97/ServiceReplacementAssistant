#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : ServiceReplacementAssistant.py
@Author: Scott
@Date  : 2020/9/20 9:33
@Desc  : 
"""
import sys
import subprocess
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtCore import pyqtSignal
from MainWin import Ui_mainWindow
from AddDialog import Ui_Dialog


def check_conf():
    try:
        with open('config.json', 'r') as jsonConf:
            json.load(jsonConf)
    except json.decoder.JSONDecodeError:
        print('[CHECK] not a good configure file, rewrite it')
        with open('config.json', 'w') as jsonConf:
            jsonConf.write('[]')
    except FileNotFoundError:
        print('[CHECK] no configure file, create one')
        with open('config.json', 'w') as jsonConf:
            jsonConf.write('[]')


class DialogWin(QDialog, Ui_Dialog):
    addSignal = pyqtSignal(str)

    def __init__(self):
        super(DialogWin, self).__init__()
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.add_item)

    def add_item(self):
        check_conf()
        # 读取当前配置
        with open('config.json', 'r') as jsonConf:
            jsonArr = json.load(jsonConf)
        curName = self.lineEdit.text()
        # 查找是否已有配置条目
        for i in range(len(jsonArr)):
            if curName == jsonArr[i]['name']:
                print('[EXISTS] ' + jsonArr[i]['name'])
                return
        # 添加配置条目
        jsonObj = {'name': curName, 'path': '',
                   'compile': '', 'host': '', 'container': ''}
        jsonArr.append(jsonObj)
        # 写配置文件
        with open('config.json', 'w+') as jsonConf:
            json.dump(jsonArr, jsonConf)
        self.addSignal.emit(curName)


class MainWin(QMainWindow, Ui_mainWindow):
    def __init__(self):
        super(MainWin, self).__init__()

        self.dia = DialogWin()
        self.bashPath = 'C:\\Program Files\\Git\\usr\\bin\\'

        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        self.load_conf()
        self.checkout_conf(self.NameComboBox.currentText())

        self.StoreButton.clicked.connect(self.store_info)
        self.ReplaceButton.clicked.connect(self.replace_service)
        self.AddPushButton.clicked.connect(self.add_conf)
        self.NameComboBox.currentTextChanged.connect(self.checkout_conf)

    def load_conf(self):
        check_conf()
        with open('config.json', 'r') as jsonConf:
            jsonArr = json.load(jsonConf)
        self.NameComboBox.clear()
        for item in jsonArr:
            self.NameComboBox.addItem(item['name'])
        # 打印日志
        # self.LogTextBrowser.setText(str(jsonArr))

    def store_info(self):
        check_conf()
        isUpdate = False
        curName = self.NameComboBox.currentText()
        # 读取当前配置
        with open('config.json', 'r') as jsonConf:
            jsonArr = json.load(jsonConf)
        # 更新配置条目
        for i in range(len(jsonArr)):
            if curName == jsonArr[i]['name']:
                print('[UPDATE] ' + jsonArr[i]['name'])
                isUpdate = True
                jsonArr[i] = {'name': curName, 'path': self.PathLineEdit.text(),
                              'compile': self.CompileLineEdit.text(), 'host': self.HostLineEdit.text(),
                              'container': self.ConIDLineEdit.text()}
        # 若未查询到该条目，新增配置条目
        if not isUpdate:
            print('[INSERT] ' + curName)
            jsonObj = {'name': curName, 'path': self.PathLineEdit.text(),
                       'compile': self.CompileLineEdit.text(), 'host': self.HostLineEdit.text(),
                       'container': self.ConIDLineEdit.text()}
            jsonArr.append(jsonObj)
        # 写配置文件
        with open('config.json', 'w+') as jsonConf:
            json.dump(jsonArr, jsonConf)
        # 更新配置文件
        self.load_conf()
        self.checkout_conf(curName)

    def replace_service(self):
        self.progressBar.setProperty("value", 0)
        with open('run.log', 'w+') as runLog, \
                open('err.log', 'a') as errLog:
            try:
                res = subprocess.run([self.bashPath + 'bash', './scripts/test.sh'], stdout=runLog, stderr=errLog)
                print(res)
            except:
                print('[ERROR] failed to exec cmd')
                return

            runLog.seek(0)
            self.LogTextBrowser.setText(runLog.read())
        self.progressBar.setProperty("value", 100)

    def add_conf(self):
        self.dia.show()
        # 添加后更新配置文件
        self.dia.addSignal.connect(self.checkout_conf)

    def checkout_conf(self, name):
        check_conf()
        # 读取当前配置
        with open('config.json', 'r') as jsonConf:
            jsonArr = json.load(jsonConf)
        for i in range(len(jsonArr)):
            if name == jsonArr[i]['name']:
                print('[CHECKOUT] ' + name)
                if self.NameComboBox.findText(name) == -1:
                    self.NameComboBox.addItem(name)
                self.NameComboBox.setCurrentText(name)
                self.PathLineEdit.setText(jsonArr[i]['path'])
                self.CompileLineEdit.setText(jsonArr[i]['compile'])
                self.HostLineEdit.setText(jsonArr[i]['host'])
                self.ConIDLineEdit.setText(jsonArr[i]['container'])
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())
