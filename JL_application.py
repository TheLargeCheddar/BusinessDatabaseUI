import sys
import psycopg2
from PyQt5.QtWidgets import QMainWindow, QApplication, QComboBox, QListWidget, QTableWidget, QTableWidgetItem
from PyQt5 import uic

qtCreatorFile = "MyUI.ui" 

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class myApp(QMainWindow):
    def __init__(self):
        super(myApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.conn = psycopg2.connect(database="milestone1db", user="postgres", password="leeper100", host="127.0.0.1", port="5432")
        self.cursor = self.conn.cursor()
        self.populate_states()

        self.ui.stateComboBox.currentIndexChanged.connect(self.state_changed)
        self.ui.cityListWidget.itemSelectionChanged.connect(self.city_changed)
        self.ui.zipcodeListWidget.itemSelectionChanged.connect(self.zipcode_changed)
        self.ui.categoryListWidget.itemSelectionChanged.connect(self.category_changed)

    def populate_states(self):
        self.cursor.execute("SELECT DISTINCT state FROM businesses ORDER BY state;")
        states = self.cursor.fetchall()
        self.ui.stateComboBox.addItem("Select State")
        for state in states:
            self.ui.stateComboBox.addItem(state[0])

    def state_changed(self):
        state = self.ui.stateComboBox.currentText()
        if state != "Select State":
            self.cursor.execute("SELECT DISTINCT city FROM businesses WHERE state=%s ORDER BY city;", (state,))
            cities = self.cursor.fetchall()
            self.ui.cityListWidget.clear()
            for city in cities:
                self.ui.cityListWidget.addItem(city[0])

    def city_changed(self):
        state = self.ui.stateComboBox.currentText()
        city = self.ui.cityListWidget.currentItem().text()
        self.cursor.execute("SELECT DISTINCT postal_code FROM businesses WHERE state=%s AND city=%s ORDER BY postal_code;", (state, city))
        zipcodes = self.cursor.fetchall()
        self.ui.zipcodeListWidget.clear()
        for zipcode in zipcodes:
            self.ui.zipcodeListWidget.addItem(zipcode[0])

    def zipcode_changed(self):
        zipcode = self.ui.zipcodeListWidget.currentItem().text()
        self.cursor.execute("SELECT DISTINCT category FROM businesses, unnest(string_to_array(categories, ',')) AS category WHERE postal_code = %s ORDER BY category;", (zipcode,))
        categories = self.cursor.fetchall()
        self.ui.categoryListWidget.clear()
        for category in categories:
            self.ui.categoryListWidget.addItem(category[0])

    def category_changed(self):
        zipcode = self.ui.zipcodeListWidget.currentItem().text()
        self.cursor.execute("SELECT name, address, city, state, stars, review_count FROM businesses WHERE postal_code=%s ORDER BY name;", (zipcode,))
        businesses = self.cursor.fetchall()
        self.ui.businessTableWidget.setRowCount(len(businesses))
        self.ui.businessTableWidget.setColumnCount(6)
        self.ui.businessTableWidget.setHorizontalHeaderLabels(["Name", "Address", "City", "State", "Stars", "Review Count"])
        for row_idx, row_data in enumerate(businesses):
            for col_idx, col_data in enumerate(row_data):
                self.ui.businessTableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = myApp()
    window.show()
    sys.exit(app.exec_())
