from geoflow.ui.window import GeoflowMainWindow
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
win = GeoflowMainWindow()
print('Window created, tree populated')
print('Tree items:', win.tree.topLevelItemCount())
root = win.tree.topLevelItem(0)
print('Root item:', root.text(0))
print('Children:', root.childCount())
for i in range(root.childCount()):
    child = root.child(i)
    print('Child:', child.text(0))
win.close()
app.quit()
