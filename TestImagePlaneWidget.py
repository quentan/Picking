#!/usr/bin/env python
# -*- coding: utf-8 -*-

# $ vtkpython TestImagePlaneWidget.py --help
# provides more details on other options.

import os
import os.path
import vtk
from vtk.test import Testing
import SimpleITK as sitk
from vtk.util import numpy_support

def read_DICOM(path_DICOM, cast_type=11):
    """
    Read a serial of DICOM images with SimpleITK,
    Cast it and return a VTK image (vtkImageData)
    Note: numpy's array order is opposite with ITK's
    :param path_DICOM: the PATH of DICOM series
    :param cast_type:
    0 - No casting
    2 - VTK_CHAR
    3 - VTK_UNSIGNED_CHAR
    4 - VTK_SHORT        
    5 - VTK_UNSIGNED_SHORT
    6 - VTK_INT
    7 - VTK_UNSIGNED_INT
    8 - VTK_LONG
    9 - VTK_UNSIGNED_LONG
    10 - VTK_FLOAT
    11 - VTK_DOUBLE   * default *
    :return: vtkImageData
    """

    # Load DICOM images
    reader = sitk.ImageSeriesReader()
    filenamesDICOM = reader.GetGDCMSeriesFileNames(path_DICOM)
    reader.SetFileNames(filenamesDICOM)
    img_sitk = reader.Execute()  # the entire 3D image is stored
    spacing = img_sitk.GetSpacing()

    # Convert SimpleITK image to numpy array
    numpy_data_array = sitk.GetArrayFromImage(img_sitk)

    # Convert numpy array to VTK array (vtkDoubleArray).
    # Note the opposite array order!
    vtk_data_array = numpy_support.numpy_to_vtk(
        num_array=numpy_data_array.transpose(2, 1, 0).ravel(),
        deep=True,
        array_type=vtk.VTK_DOUBLE)

    # Convert vtkArray to vtkImageData
    img_vtk = vtk.vtkImageData()
    img_vtk.SetDimensions(numpy_data_array.shape)
    img_vtk.SetSpacing(spacing[::-1])  # Note the order should be reversed!
    img_vtk.GetPointData().SetScalars(vtk_data_array)  # is a vtkImageData

    # No cast
    if cast_type == 0:
        return img_vtk

    # Cast the image to another data type
    elif cast_type in [i for i in range(2, 12)]:
        cast = vtk.vtkImageCast()
        cast.SetInputData(img_vtk)
        cast.SetOutputScalarType(cast_type)
        cast.Update()

        # The output of `cast` is a vtkImageData
        # `cast` is a vtkImageAlgorithm
        return cast.GetOutput()

    # Wrong cast type. Return the no-cast vtkImageData
    else:
        sys.stderr.write('Wrong Cast Type! It should be 2, 3, ..., or 11')
        return img_vtk


class TestImagePlaneWidget(Testing.vtkTest):

    def testBug(self):
        # Uncomment the next line if you want to run this via
        # `gdb python`.
        # raw_input('Hit Ctrl-C')

        # Load some data.
        v16 = vtk.vtkVolume16Reader()
        v16.SetDataDimensions(64, 64)
        v16.SetDataByteOrderToLittleEndian()
        v16.SetFilePrefix(os.path.join(Testing.VTK_DATA_ROOT,
                                       "Data", "headsq", "quarter"))
        v16.SetImageRange(1, 93)
        v16.SetDataSpacing(3.2, 3.2, 1.5)
        v16.Update()

        xMin, xMax, yMin, yMax, zMin, zMax = v16.GetExecutive().GetWholeExtent(
            v16.GetOutputInformation(0))
        img_data = v16.GetOutput()

        # **************************************************
        # Look here for wierdness.

        # Lets create this data using the data from the reader.
        my_img_data = vtk.vtkImageData()
        my_img_data.SetDimensions(img_data.GetDimensions())
#        my_img_data.SetWholeExtent(img_data.GetWholeExtent())
        my_img_data.SetExtent(img_data.GetExtent())
#        my_img_data.SetUpdateExtent(img_data.GetUpdateExtent())
        my_img_data.SetSpacing(img_data.GetSpacing())
        my_img_data.SetOrigin(img_data.GetOrigin())
        my_img_data.SetScalarType(
            img_data.GetScalarType(), my_img_data.GetInformation())
        my_img_data.GetPointData().SetScalars(
            img_data.GetPointData().GetScalars())
        # hang on to original image data.
        orig_img_data = img_data

        # hijack img_data with our own.  If you comment this out everything is
        # fine.
        # img_data = my_img_data
        # **************************************************


        # DICOM path
        path_dicom = "/Users/Quentan/Develop/IMAGE/PHENIX/CT2 tête, face, sinus/COU IV"
        # path_dicom = "/Users/Quentan/Develop/IMAGE/CTK_Dataset/Head_Axial_DICOM_2461_CTHead10"
        img_data = read_DICOM(path_dicom)


        spacing = img_data.GetSpacing()
        sx, sy, sz = spacing

        origin = img_data.GetOrigin()
        ox, oy, oz = origin

        dims = img_data.GetDimensions()
        dx, dy, dz = dims

        # An outline is shown for context.
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(img_data)

        outlineMapper = vtk.vtkPolyDataMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())

        outlineActor = vtk.vtkActor()
        outlineActor.SetMapper(outlineMapper)

        # The shared picker enables us to use 3 planes at one time
        # and gets the picking order right
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.005)

        # The 3 image plane widgets are used to probe the dataset.
        planeWidgetX = vtk.vtkImagePlaneWidget()
        planeWidgetX.DisplayTextOn()
        planeWidgetX.SetInputData(img_data)
        planeWidgetX.SetPlaneOrientationToXAxes()
        # planeWidgetX.SetSliceIndex(32)
        planeWidgetX.SetSliceIndex(dx/2)
        planeWidgetX.SetPicker(picker)
        # planeWidgetX.SetKeyPressActivationValue("x")
        prop1 = planeWidgetX.GetPlaneProperty()
        prop1.SetColor(1, 0, 0)

        planeWidgetY = vtk.vtkImagePlaneWidget()
        planeWidgetY.DisplayTextOn()
        planeWidgetY.SetInputData(img_data)
        planeWidgetY.SetPlaneOrientationToYAxes()
        # planeWidgetY.SetSliceIndex(32)
        planeWidgetY.SetSliceIndex(dy/2)
        planeWidgetY.SetPicker(picker)
        planeWidgetY.SetKeyPressActivationValue("y")
        prop2 = planeWidgetY.GetPlaneProperty()
        prop2.SetColor(1, 1, 0)
        planeWidgetY.SetLookupTable(planeWidgetX.GetLookupTable())

        # for the z-slice, turn off texture interpolation:
        # interpolation is now nearest neighbour, to demonstrate
        # cross-hair cursor snapping to pixel centers
        planeWidgetZ = vtk.vtkImagePlaneWidget()
        planeWidgetZ.DisplayTextOn()
        planeWidgetZ.SetInputData(img_data)
        planeWidgetZ.SetPlaneOrientationToZAxes()
        # planeWidgetZ.SetSliceIndex(46)
        planeWidgetZ.SetSliceIndex(dz/2)
        planeWidgetZ.SetPicker(picker)
        planeWidgetZ.SetKeyPressActivationValue("z")
        prop3 = planeWidgetZ.GetPlaneProperty()
        prop3.SetColor(0, 0, 1)
        planeWidgetZ.SetLookupTable(planeWidgetX.GetLookupTable())

        # Create the RenderWindow and Renderer
        ren = vtk.vtkRenderer()
        renWin = vtk.vtkRenderWindow()
        # renWin.SetMultiSamples(0)
        renWin.AddRenderer(ren)

        # Add the outline actor to the renderer, set the background
        # color and size
        ren.AddActor(outlineActor)
        renWin.SetSize(600, 600)
        ren.SetBackground(0.1, 0.1, 0.2)

        current_widget = planeWidgetZ
        mode_widget = planeWidgetZ

        # Set the interactor for the widgets
        iact = vtk.vtkRenderWindowInteractor()
        # iact = renWin.GetInteractor()
        iact.SetRenderWindow(renWin)
        planeWidgetX.SetInteractor(iact)
        planeWidgetX.On()
        planeWidgetY.SetInteractor(iact)
        planeWidgetY.On()
        planeWidgetZ.SetInteractor(iact)
        planeWidgetZ.On()

        # Create an initial interesting view
        ren.ResetCamera()
        cam1 = ren.GetActiveCamera()
        cam1.Elevation(110)
        cam1.SetViewUp(0, 0, -1)
        cam1.Azimuth(45)
        ren.ResetCameraClippingRange()

        iact.Initialize()
        iact.Start()
        renWin.Render()

if __name__ == "__main__":
    Testing.main([(TestImagePlaneWidget, 'test')])
