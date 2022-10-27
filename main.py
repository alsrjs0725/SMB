from pynput import keyboard
from generator import Config, Note, Chart
from PyQt5 import QtWidgets, QtGui, QtCore
from forms import KeyMappingWindow, Ui_MainWindow
import time


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        QtGui.QFontDatabase.addApplicationFont('./src/BM JUA_TTF.ttf')
        self.recording = False
        self.chart = Chart()
        self.pressed = dict()
        self.curselection = None
        self.keymapping_window = KeyMappingWindow(MainWindow=self)
        self.keymapping = {}
        
    def setupUi(self, ui:Ui_MainWindow):
        self.ui = ui
        ui.setupUi(self)
        
    def get_key_text(self, key):
        return str(key).strip('\'')
        
    def get_key_vk(self, key):
        if type(key) is keyboard.Key:
            key = key.value
        return key.vk

    def toggleRecord(self):
        self.recording = not self.recording
        if self.recording:
            self.chart = Chart()
            self.ui.saveAsBMSBtn.setEnabled(False)
            self.ui.saveBtn.setEnabled(False)
            self.ui.loadBtn.setEnabled(False)
            self.ui.toggleRecordBtn.setText('녹화 중단')
        else:
            for vk in self.pressed:
                self.chart.add_note(Note(vk, round(self.pressed[vk], 4), round(time.time() - self.pressed[vk], 4)))
            self.pressed = dict()
            self.ui.saveAsBMSBtn.setEnabled(True)
            self.ui.saveBtn.setEnabled(True)
            self.ui.loadBtn.setEnabled(True)
            self.ui.toggleRecordBtn.setText('녹화 시작')
            print(self.chart)

    def on_press(self, key):
        vk = self.get_key_vk(key)
        if vk in self.pressed:
            return
        self.pressed[vk] = time.time()
        if not (self.curselection is None):
            self.curselection.setText(self.get_key_text(key))
            self.keymapping[self.curselection.objectName()] = vk
            self.curselection = None
            self.keymapping_window.hide()
            
        
    def on_release(self, key):
        vk = self.get_key_vk(key)
        if self.recording:
            self.chart.add_note(Note(vk, round(self.pressed[vk], 4), round(time.time() - self.pressed[vk], 4)))
        if vk in self.pressed:
            self.pressed.pop(vk)
            
    def load(self):
        dir_ = QtWidgets.QFileDialog.getOpenFileName(filter='Replay File(*.replay)')
        if dir_[0] == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText('불러오기 실패')
            msg.setWindowTitle('불러오기')
            msg.show()
            msg.exec_()
            return
        self.chart = Chart()
        with open(dir_[0], 'r') as file:
            for line in file.readlines():
                vk, start, duration = line.split(',')
                self.chart.add_note(Note(int(vk), float(start), float(duration)))
        self.ui.saveAsBMSBtn.setEnabled(True)
        self.ui.saveBtn.setEnabled(True)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('불러오기 성공')
        msg.setWindowTitle('불러오기')
        msg.show()
        msg.exec_()
    
    def save(self):
        dir_ = QtWidgets.QFileDialog.getSaveFileName(filter='Replay File(*.replay)')
        if dir_[0] == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText('저장 실패')
            msg.setWindowTitle('저장')
            msg.show()
            msg.exec_()
            return
        with open(dir_[0], 'w') as fos:
            for notes in self.chart.notes.values():
                for note in notes:
                    if not (type(note) is Note):
                        continue
                    fos.write(f'{note.key},{note.start_time},{note.duration}\n')
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('저장 성공')
        msg.setWindowTitle('저장')
        msg.show()
        msg.exec_()
        
    
    def saveAsBMS(self):
        dir_ = QtWidgets.QFileDialog.getSaveFileName(filter='BMS(*.bms *.bme *.bml)')
        if dir_[0] == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText('저장 실패')
            msg.setWindowTitle('저장')
            msg.show()
            msg.exec_()
            return
        config = Config(
            title='title',
            artist='artist',
            keymapping=self.keymapping
        )
        self.chart.write(dir_[0], config)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText('저장 성공')
        msg.setWindowTitle('저장')
        msg.show()
        msg.exec_()
    
    def keyMapping(self, btn:QtWidgets.QPushButton):
        self.keymapping_window.show()
        self.curselection = btn
    
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.keymapping_window.close()
        return super().closeEvent(a0)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    ui = Ui_MainWindow()
    main_window.setupUi(ui)
    main_window.show()
    
    listener = keyboard.Listener(
        on_press=main_window.on_press,
        on_release=main_window.on_release)
    listener.start()
    sys.exit(app.exec_())