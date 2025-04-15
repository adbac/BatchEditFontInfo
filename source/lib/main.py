import AppKit
import ezui
from mojo.roboFont import AllFonts
from mojo.subscriber import Subscriber, registerCurrentFontSubscriber
from mojo.UI import PostBannerNotification


class BatchEditFontInfoWindow(Subscriber, ezui.WindowController):

    debug = True

    def build(self):

        content = """
        Select the attributes you want to update in all open UFO files.

        | ------------- |  @table
        | list          |
        | ------------- |

        ======================

        (Update)    @updateButton
        """

        descriptionData = dict(
            table=dict(
                items=[],
                allowsMultipleSelection=True,
                allowsEmptySelection=False,
                alternatingRowColors=True,
                columnDescriptions=[
                    dict(
                        identifier="attribute",
                        title="Attribute",
                        # width=50,
                        editable=False,
                    ),
                    dict(
                        identifier="oldValue",
                        title="Old value",
                        # width=50,
                        editable=False,
                    ),
                    dict(
                        identifier="newValue",
                        title="New value",
                        # width=50,
                        editable=False,
                    ),
                ],
            ),
            # cancelButton = dict(
            #     keyEquivalent=chr(27)  # call button on esc keydown
            # )
        )

        self.w = ezui.EZWindow(
            minSize=(400, 400),
            size=(500, 400),
            title="Batch Edit Font Info",
            content=content,
            descriptionData=descriptionData,
            controller=self,
            defaultButton="updateButton",
        )

        self.changes = {}

    def started(self):
        self.w.open()

    def currentFontInfoDidChangeValue(self, info):
        table = self.w.getItem("table")
        self.changes.update(info["changedInfoAttributes"])
        items = table.get()
        newItems = []
        for attribute, valuesInfo in self.changes.items():
            oldValue = str(valuesInfo["oldValue"]).replace("\n", " ")
            newValue = str(valuesInfo["newValue"]).replace("\n", " ")
            if attribute in [item["attribute"] for item in items]:
                index = self.getItemIndexForAttribute(items, attribute)
                table.setItemValue(index, "newValue", newValue)
            else:
                newItems.append(
                    dict(
                        attribute=attribute,
                        oldValue=oldValue,
                        newValue=newValue,
                    )
                )
        table.appendItems(newItems)

    def getItemIndexForAttribute(self, items, attribute):
        for index, item in enumerate(items):
            if item["attribute"] == attribute:
                return index
        return None
    
    def tableDoubleClickCallback(self, sender):
        table = self.w.getItem("table")
        if not table.get():
            return
        index = sender.getSelectedIndexes()[0]
        item = sender.getSelectedItems()[0]
        popover = FullInfoPopover(item["oldValue"], item["newValue"])
        table.openPopoverAtIndex(popover, index + 1)

    def updateButtonCallback(self, sender):
        table = self.w.getItem("table")
        items = table.get()
        if not items:
            return
        attributes = {attribute: valuesInfo["newValue"] for attribute, valuesInfo in self.changes.items()}
        for font in AllFonts():
            font.info.update(attributes)
            font.changed()
        PostBannerNotification("Batch Edit Font Info", f"Updated {len(attributes.keys())} font info attribute(s) in {len(AllFonts())} UFO file(s)")

class FullInfoPopover(ezui.WindowController):

    def build(self, oldText, newText):
        content = f"""
        !§ Old value
        [[_~{oldText}~_]]   @old
        !§ New value
        [[_~{newText}~_]]   @new
        """
        
        self.w = ezui.EZPopover(
            size=(320, 200),
            content=content,
            controller=self
        )

        for id in ["old", "new"]:
            self.w.getItem(id).setFont(
                name="system-monospaced",
                size=12,
            )

        # self.w.getItem("title").getNSTextField().setFont_(AppKit.NSFont.monospacedSystemFontOfSize_weight_(14, AppKit.NSFontWeightSemibold))

    def open(self, parent, location):
        self.w.open(parent, "right", location)

registerCurrentFontSubscriber(BatchEditFontInfoWindow)