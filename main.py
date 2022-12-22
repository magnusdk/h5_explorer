import os
import sys
from dataclasses import dataclass
from typing import Iterable

import h5py
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Tree, TreeNode, Header


@dataclass
class H5NodeData:
    path: Iterable[str]  # Path to the node in the .h5 file
    is_loaded: bool = False


class H5Tree(Tree):
    BINDINGS = [
        Binding("enter", "select_cursor", "Toggle node"),
        Binding("left, right", "select_cursor", "Toggle node", show=False),
        Binding("up", "cursor_up", "Cursor Up"),
        Binding("down", "cursor_down", "Cursor Down"),
    ]

    def __init__(self, filepath: str):
        # Set the root node to be the filename
        super().__init__(os.path.basename(filepath), data=H5NodeData(()))
        self.file = h5py.File(filepath, "r")
        self.root.expand()

    def _at_path(self, path: Iterable[str]) -> h5py.HLObject:
        "Get the thing at the given path in the .h5 file"
        thing = self.file
        for key in path:
            thing = thing[key]
        return thing

    def _load_node(self, node: TreeNode):
        "Load the children of the given node if they have not been loaded before."
        data: H5NodeData = node.data
        if data and not data.is_loaded:
            data.is_loaded = True  # Do not load it again
            if isinstance(self._at_path(data.path), h5py.Group):
                # If it is a h5py.Group, it will have a set of subgroups
                for key in self._at_path(data.path).keys():
                    node.add(key, data=H5NodeData(data.path + (key,)))
            else:
                # Else, we just show it as a leaf node
                node.add(str(self._at_path(data.path)), allow_expand=False)

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        self._load_node(event.node)

    def on_mount(self):
        self._load_node(self.root)


class H5Explorer(App):
    def __init__(self, filepath: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filepath = filepath

    def compose(self) -> ComposeResult:
        yield Header()
        yield H5Tree(self.filepath)
        yield Footer()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <h5_file>")
        sys.exit(1)
    filename = sys.argv[1]

    app = H5Explorer(filename)
    app.run()
