from pymxs import runtime as rt
import json, os

from PySide2.QtWidgets import QMenu

MXS_MATERIAL_CLASS = rt.execute("material")
MXS_GEOMETRY_CLASS = rt.execute("geometryclass")
MXS_MODIFIER_CLASS = rt.execute("modifier")

class Helpers(object):
    def getSettings(self):
        """
        @name: getSettings
        @desc: Gets the settings from the settings .json file.
        @returns {dictionary}
        """
        # Open the .json file and load the data into a dictionary
        with open(os.path.dirname(os.path.realpath(__file__)) + "\\settings.json") as f:
            data = json.load(f)

        # Return the dictionary of data
        return data

    def getMenu(self, treeView):
        model = treeView.model()

        # This is getting the selected indexes of the proxy model attached
        # to the tree view. This is not to be confused with the source
        # model, which is the actual AssetListModel.
        indexes = treeView.selectedIndexes()
        context = None

        if len(indexes) == 0:
            return

        # Get the actual item(s) selected
        items = []
        for proxyIndex in indexes:
            proxyModel = model
            sourceIndex = proxyModel.mapToSource(proxyIndex)
            sourceModel = proxyModel.sourceModel()
            item = sourceModel.getItem(sourceIndex)

            items.append(item)

        # Get the depth of the item(s) selected
        if len(indexes) > 0:
            depth = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                depth += 1

        # Create a new menu
        menu = QMenu()

        # Depending on the depth of the selection, add different actions
        if depth == 0:
            menu.addAction("Reveal in explorer...")
            menu.addAction("Set path...")

        if depth == 1:
            menu.addAction("Select all children")

        if depth == 2:
            if item.context() == "Materials":
                menu.addAction("Open in SME")

            if item.context() == "Geometry":
                menu.addAction("Select object(s)")

            if item.context() == "Modifiers":
                menu.addAction("Select parent object(s)")

        return menu


    def getAssetRefs(self, filename):
        """
        @name: getAssetRefs
        @desc: Gets all references in the scene, based on the BitmapClasses list
            from the settings .json file. This returns a dictionary with the
            materials, geometry, and modifiers associated with the filename.
        @param {string} filename: The full filename to get all references from
        @returns {dictionary}
        """
        # Get the .json settings first. This'll list all of the classes to
        # iterate through, and what their respective 'filename' parameter
        # is called.
        data = self.getSettings()

        materials = []
        geometry  = []
        modifiers = []

        # Iterates through the different MAXScript classes to check through
        for classKey in data["BitmapClasses"]:

            # Get the respective class' denoted 'filename' parameter
            # These vary a bit per class
            paramNames = data["BitmapClasses"][classKey]

            # Get the MAXScript Value of the class
            classValue = rt.execute(classKey)

            # Create an empty list of the nodes we'll look through
            nodes = []

            # If it DOES exist, meaning the standard or 3rd party plugins
            # are found (Max, Arnold, V-Ray, etc.)
            if classValue != None:

                # Get all the instances of that node
                instances = rt.GetClassInstances(classValue)

                for inst in instances:
                    # If that node matches the same filename we're currently
                    # checking against, then it's a match!
                    try:
                        for param in paramNames:
                            if (rt.getProperty(inst, param)) == filename:
                                nodes.append(inst)
                    except:
                        pass

            # If we've found 1 or more matching nodes, we'll iterate through them
            if len(nodes) > 0:
                for node in nodes:

                    # Get the node's dependents. This'll be a giant array of every
                    # dependent found in the scene, which'll include a bunch of
                    # nonsense nodes.
                    deps = rt.refs.dependents(node)

                    # Filter through each dependent and add to each respective list
                    # whether it's a subclass of materials, geometry, or modifiers.
                    for dep in deps:
                        if rt.superClassOf(dep) == MXS_MATERIAL_CLASS:
                            materials.append(dep)
                        if rt.superClassOf(dep) == MXS_GEOMETRY_CLASS:
                            geometry.append(dep)
                        if rt.superClassOf(dep) == MXS_MODIFIER_CLASS:
                            modifiers.append(dep)

                # Return the mapped dictionary of nodes we found
                return  {
                            "Materials" : materials,
                            "Geometry" : geometry,
                            "Modifiers": modifiers
                        }

        # If we didn't find anything, return an empty dictionary
        return {}