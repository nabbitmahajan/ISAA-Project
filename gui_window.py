from PyQt5 import QtCore, QtGui, QtWidgets
from os import path
from datetime import datetime
from image_processing import Image, np, reconstruct_image, split_parts_list
from scheme import Scheme


class Ui_SecretSharingEncryption(object):
    def __init__(self):
        self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "The divisions are incomplete")

    def browse_img(self):
        while True:
            pname, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Select an image", '.', "(*.tif *.tiff *.jpg *.jpeg *.gif *.png *.bmp *.eps *.raw *.cr2" "*.nef *.orf *.sr2)")
            print(pname)
            if pname is not None:
                break
            image_profile = QtGui.QImage(pname)  # QImage object
            image_profile = image_profile.scaled(331, 251, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            # scaling the image to 331x251 and preserving the aspect ratio
            self.label_29.setPixmap(QtGui.QPixmap.fromImage(image_profile))
            self.path_image = pname
            self.dir_name = path.dirname(pname)

    def encrypt_img(self):
        self.listWidget.clear()
        if self.label_29.pixmap() is None:
            self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Please enter a picture")
            self.error_message.exec_()
        elif self.spinBox.value() == 0 or self.spinBox.value() < self.spinBox_2.value() or \
                self.spinBox_2.value() == 0 or self.spinBox.value() < 2 or self.spinBox_2.value() < 2:
            self.error_message.exec_()
        else:
            self.img_name, self.ext = path.splitext(self.path_image)
            t1 = datetime.now()
            pic = Image.open(self.path_image)
            matrix = np.array(pic, np.int32)
            self.sharesRGB = split_parts_list(self.spinBox.value(), self.spinBox_2.value(), 257, matrix, self.path_image)
            print("Time to create divisions: ")
            print((datetime.now() - t1).seconds)
            self.label_5.setText(self.dir_name)
            i = 0
            for v in range(self.spinBox.value()):
                share_path = self.img_name + "_share" + str(i) + ".png"
                i += 1
                self.listWidget.addItem(share_path)

    def add_share(self):
        if self.label_29.pixmap() is None:
            self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Image not encrypted")
            self.error_message.exec_()
        elif self.spinBox.value() == 0 or self.spinBox.value() < self.spinBox_2.value() or\
                self.spinBox_2.value() == 0 or self.spinBox.value() < 3 or self.spinBox_2.value() < 2:
            self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Some of the number of divisions is incomplete")
            self.error_message.exec_()
        else:
            imgs = []
            for i in range(self.spinBox_2.value()):
                pname, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Select an Image", '', "(*.png)")
                if pname is not None and pname is not "":
                    imgs.append(pname)
                    self.listWidget_2.addItem(pname)
            self.shares_for_reconstruction = imgs

    def decrypt_images(self):
        if self.label_29.pixmap() is None:
            self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Image not encrypted")
            self.error_message.exec_()
        elif self.spinBox.value() == 0 or self.spinBox.value() < self.spinBox_2.value() or\
                self.spinBox_2.value() == 0 or self.spinBox.value() < 3 or self.spinBox_2.value() < 2:
            self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Some of the number of divisions is not complete")
            self.error_message.exec_()
        elif self.listWidget_2.count() < self.spinBox_2.value():
            self.error_message = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Not enough images entered")
            self.error_message.exec_()
        else:
            matrix = reconstruct_image(self.shares_for_reconstruction, self.spinBox_2.value(), 257, self.sharesRGB)
            new_img = Image.fromarray(matrix.astype('uint8'), 'RGB')
            new_img.save(self.img_name + "_SECRET" + self.ext)
            image_profile = QtGui.QImage(self.img_name + "_SECRET" + self.ext)  # QImage object
            image_profile = image_profile.scaled(331, 251, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation)
            # scaling the image to 331x251 and preserving the aspect ratio
            self.label_30.setPixmap(QtGui.QPixmap.fromImage(image_profile))
            self.listWidget_2.clear()
