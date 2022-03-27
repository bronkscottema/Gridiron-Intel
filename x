#push {
    color: white;
    background-color: #041E42; /*primary*/
    border :3px outset;
    border-color: #A89968;
    border-radius: 5px;
    max-width: 260px;
    min-width: 200px;
}

QComboBox {
    max-width: 250px;
    min-width: 200px;
    padding: 5px;
    border-style: outset;
    border-width: 2px;
    border-radius: 5px;
    border-color: #041E42; /*primary*/
}

QComboBox::drop-down {
    border: 0px; /* This seems to replace the whole arrow of the combo box */
}

/* combobox dropdown arrow image?
QComboBox::down-arrow {
    image: url("images/arrow.png");
    width: 25px;
    height: 32px;
    padding-right: 5px;
}
*/

QTableView {
    alternate-background-color: #A89968;
    selection-background-color: #041E42; /*primary*/
}

QTableCornerButton {
    background-color: #041E42; /*primary*/
}

QHeaderView::section {
    background-color: #041E42; /*primary*/
    border: 0.5px solid white;
    color: white;
}

QComboBox QAbstractItemView {
    selection-background-color: #A89968;
}