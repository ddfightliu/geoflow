from geoflow.ui.window import GeoflowMainWindow
from PySide6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
win = GeoflowMainWindow()
print('Window created')

# Find a file item in the tree
root = win.tree.topLevelItem(0)
for i in range(root.childCount()):
    child = root.child(i)
    if child.text(0) == 'README.md':
        print('Found README.md, opening...')
        win.open_file_from_tree(child)
        break

print('Tabs after opening:', win.tabs.count())
if win.tabs.count() > 0:
    print('Tab title:', win.tabs.tabText(0))

win.close()
app.quit()
