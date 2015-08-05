#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Using vtkImagePlaneWidget to pick up points from image.
"""

import sys
import vtk
import SimpleITK as sitk
from vtk.util import numpy_support

# START - Constants

# DICOM path
# path_dicom = "/Users/Quentan/Develop/IMAGE/PHENIX/CT2 tête, face, sinus/COU IV"
path_dicom = "/Users/Quentan/Develop/IMAGE/CTK_Dataset/Head_Axial_DICOM_2461_CTHead10"
# path_dicom = "/Users/Quentan/Develop/IMAGE/medical data/5.25 SnapShot
# Segment 0.625 mm 56-69 BPM - Large/dcm/4"  # lung

# END - Constants

# Initialisation
render_window = vtk.vtkRenderWindow()
iren = vtk.vtkRenderWindowInteractor()
renderer = vtk.vtkRenderer()


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


def read_meta_image(meta_name, cast_type=5):
    """
    Usually Meta Image is `unsigned short`
    No casting leads to wrong reslut!
    """
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(meta_name)

    # No cast
    if cast_type == 0:
        # vtkImageData with wrong dims and bounds value.
        return reader.GetOutput()

    # Cast the image to another data type
    elif cast_type in [i for i in range(2, 12)]:
        cast = vtk.vtkImageCast()
        # cast.SetInputData(img_vtk)
        cast.SetInputConnection(reader.GetOutputPort())
        cast.SetOutputScalarType(cast_type)
        cast.Update()
        return cast.GetOutput()  # The output of `cast` is a vtkImageData

    # Wrong cast type. Return the no-cast vtkImageData
    else:
        sys.stderr.write('Wrong Cast Type! It should be 2, 3, ..., or 11')
        return reader.GetOutput()


def vtk_show(_renderer, window_name='VTK Show Window',
             width=640, height=480, has_picker=False):
    """
    Show the vtkRenderer in an vtkRenderWindow
    Only support ONE vtkRenderer
    :return: No return value
    """
    # render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(_renderer)
    render_window.SetSize(width, height)
    render_window.Render()
    # It works only after Render() is called
    render_window.SetWindowName(window_name)

    # iren = vtk.vtkRenderWindowInteractor()
    # iren.SetRenderWindow(render_window)

    interactor_style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(interactor_style)

    # Add an Annoted Cube with Arrows
    cube = vtk.vtkAnnotatedCubeActor()
    cube.SetXPlusFaceText('R')
    cube.SetXMinusFaceText('L')
    cube.SetYPlusFaceText('A')
    cube.SetYMinusFaceText('P')
    cube.SetZPlusFaceText('I')
    cube.SetZMinusFaceText('S')
    cube.SetXFaceTextRotation(180)
    cube.SetYFaceTextRotation(180)
    cube.SetZFaceTextRotation(-90)
    cube.SetFaceTextScale(0.65)
    cube.GetCubeProperty().SetColor(0.5, 1.0, 1.0)
    cube.GetTextEdgesProperty().SetLineWidth(1)
    cube.GetTextEdgesProperty().SetColor(0.18, 0.28, 0.23)
    cube.GetTextEdgesProperty().SetDiffuse(0)
    cube.GetTextEdgesProperty().SetAmbient(1)

    cube.GetXPlusFaceProperty().SetColor(1, 0, 0)
    cube.GetXPlusFaceProperty().SetInterpolationToFlat()
    cube.GetXMinusFaceProperty().SetColor(1, 0, 0)
    cube.GetXMinusFaceProperty().SetInterpolationToFlat()

    cube.GetYPlusFaceProperty().SetColor(0, 1, 0)
    cube.GetYPlusFaceProperty().SetInterpolationToFlat()
    cube.GetYMinusFaceProperty().SetColor(0, 1, 0)
    cube.GetYMinusFaceProperty().SetInterpolationToFlat()

    cube.GetZPlusFaceProperty().SetColor(0, 0, 1)
    cube.GetZPlusFaceProperty().SetInterpolationToFlat()
    cube.GetZMinusFaceProperty().SetColor(0, 0, 1)
    cube.GetZMinusFaceProperty().SetInterpolationToFlat()

    text_property = vtk.vtkTextProperty()
    text_property.ItalicOn()
    text_property.ShadowOn()
    text_property.BoldOn()
    text_property.SetFontFamilyToTimes()
    text_property.SetColor(1, 0, 0)

    text_property_2 = vtk.vtkTextProperty()
    text_property_2.ShallowCopy(text_property)
    text_property_2.SetColor(0, 1, 0)
    text_property_3 = vtk.vtkTextProperty()
    text_property_3.ShallowCopy(text_property)
    text_property_3.SetColor(0, 0, 1)

    axes = vtk.vtkAxesActor()
    axes.SetShaftTypeToCylinder()
    axes.SetXAxisLabelText('X')
    axes.SetYAxisLabelText('Y')
    axes.SetZAxisLabelText('Z')
    axes.SetTotalLength(1.5, 1.5, 1.5)
    axes.GetXAxisCaptionActor2D().SetCaptionTextProperty(text_property)
    axes.GetYAxisCaptionActor2D().SetCaptionTextProperty(text_property_2)
    axes.GetZAxisCaptionActor2D().SetCaptionTextProperty(text_property_3)

    assembly = vtk.vtkPropAssembly()
    assembly.AddPart(axes)
    assembly.AddPart(cube)

    marker = vtk.vtkOrientationMarkerWidget()
    marker.SetOutlineColor(0.93, 0.57, 0.13)
    marker.SetOrientationMarker(assembly)
    marker.SetViewport(0.0, 0.0, 0.15, 0.3)
    marker.SetInteractor(iren)
    marker.EnabledOn()
    marker.InteractiveOn()

    # Add a x-y-z coordinate to the original point
    axes_coor = vtk.vtkAxes()
    axes_coor.SetOrigin(0, 0, 0)
    mapper_axes_coor = vtk.vtkPolyDataMapper()
    mapper_axes_coor.SetInputConnection(axes_coor.GetOutputPort())
    actor_axes_coor = vtk.vtkActor()
    actor_axes_coor.SetMapper(mapper_axes_coor)
    _renderer.AddActor(actor_axes_coor)

    # Add an original point and text
    add_point(_renderer, color=[0, 1, 0], radius=2)
    add_text(_renderer, position=[0, 0, 0], text="Origin",
             color=[0, 1, 0], scale=2)

    _renderer.ResetCamera()  # Coorperate with vtkFollower

    # iren.Initialize()  # will be called by Start() autometically
    if has_picker:
        iren.AddObserver('MouseMoveEvent', MoveCursor)
    iren.Start()


def add_point(_renderer, position=[0, 0, 0], color=[0.4, 0.4, 0.4], radius=0.2):
    _point = vtk.vtkSphereSource()
    _point.SetCenter(position)
    _point.SetRadius(radius)
    _point.SetPhiResolution(10)
    _point.SetThetaResolution(10)

    _mapper_point = vtk.vtkPolyDataMapper()
    _mapper_point.SetInputConnection(_point.GetOutputPort())

    _actor_point = vtk.vtkActor()
    _actor_point.SetMapper(_mapper_point)
    _actor_point.GetProperty().SetColor(color)

    _renderer.AddActor(_actor_point)


def add_text(_renderer, position, text="TEXT", color=[0.5, 0.5, 0.5], scale=0.1):
    # Create text with the x-y-z coordinate system
    _text = vtk.vtkVectorText()
    _text.SetText(text)
    mapper_text = vtk.vtkPolyDataMapper()
    mapper_text.SetInputConnection(_text.GetOutputPort())
    # actor_text_origin = vtk.vtkActor()
    actor_text = vtk.vtkFollower()
    actor_text.SetCamera(_renderer.GetActiveCamera())
    actor_text.SetMapper(mapper_text)
    actor_text.SetScale(scale, scale, scale)
    actor_text.GetProperty().SetColor(color)
    # plus of 2 arrays
    actor_text.AddPosition([sum(x) for x in zip(position, [0, -0.1, 0])])

    _renderer.AddActor(actor_text)


def get_plane_widget(input_data, axis=0, slice_idx=10, color=[1, 0, 0], key_value='i'):
    plane_widget = vtk.vtkImagePlaneWidget()
    plane_widget.DisplayTextOn()
    plane_widget.SetInputData(input_data)
    plane_widget.SetPlaneOrientation(axis)
    plane_widget.SetSliceIndex(slice_idx)

    picker = vtk.vtkCellPicker()
    picker.SetTolerance(0.005)
    plane_widget.SetPicker(picker)

    plane_widget.SetKeyPressActivationValue(key_value)
    plane_widget.GetPlaneProperty().SetColor(color)

    return plane_widget


reader = read_DICOM(path_dicom)

# Some informaion of the image
dims = reader.GetDimensions()
bounds = reader.GetBounds()
spacing = reader.GetSpacing()
origin = reader.GetOrigin()

# Outline
outline = vtk.vtkOutlineFilter()
outline.SetInputData(reader)

mapper_outline = vtk.vtkPolyDataMapper()
mapper_outline.SetInputConnection(outline.GetOutputPort())

actor_outline = vtk.vtkActor()
actor_outline.SetMapper(mapper_outline)

# vtkImagePlaneWidgets
# plane_widget_x = get_plane_widget(reader, axis=0, slice_idx=dims[0] / 2,
#                                   color=[1, 0, 0], key_value='x')
# plane_widget_y = get_plane_widget(reader, axis=1, slice_idx=dims[1] / 2,
#                                   color=[1, 1, 0], key_value='y')
# plane_widget_y.SetLookupTable(plane_widget_x.GetLookupTable())

# plane_widget_z = get_plane_widget(reader, axis=2, slice_idx=dims[2] / 2,
#                                   color=[0, 0, 1], key_value='z')
# plane_widget_z.SetLookupTable(plane_widget_x.GetLookupTable())


# Set the interactor for the widgets
# iren.SetRenderWindow(render_window)
# plane_widget_x.SetInteractor(iren)
# plane_widget_x.On()
# plane_widget_y.SetInteractor(iren)
# plane_widget_y.On()
# plane_widget_z.SetInteractor(iren)
# plane_widget_z.On()


img_data = reader
# The shared picker enables us to use 3 planes at one time
# and gets the picking order right
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.005)

# The 3 image plane widgets are used to probe the dataset.
planeWidgetX = vtk.vtkImagePlaneWidget()
planeWidgetX.DisplayTextOn()
planeWidgetX.SetInputData(img_data)
planeWidgetX.SetPlaneOrientationToXAxes()
planeWidgetX.SetSliceIndex(32)
planeWidgetX.SetPicker(picker)
planeWidgetX.SetKeyPressActivationValue("x")
prop1 = planeWidgetX.GetPlaneProperty()
prop1.SetColor(1, 0, 0)

planeWidgetY = vtk.vtkImagePlaneWidget()
planeWidgetY.DisplayTextOn()
planeWidgetY.SetInputData(img_data)
planeWidgetY.SetPlaneOrientationToYAxes()
planeWidgetY.SetSliceIndex(32)
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
planeWidgetZ.SetSliceIndex(46)
planeWidgetZ.SetPicker(picker)
planeWidgetZ.SetKeyPressActivationValue("z")
prop3 = planeWidgetZ.GetPlaneProperty()
prop3.SetColor(0, 0, 1)
planeWidgetZ.SetLookupTable(planeWidgetX.GetLookupTable())

# VTK Rendering
render_window.AddRenderer(renderer)
render_window.SetMultiSamples(0)

renderer.AddActor(actor_outline)

# Set the interactor for the widgets
iact = vtk.vtkRenderWindowInteractor()
# iact = renWin.GetInteractor()
iact.SetRenderWindow(render_window)
planeWidgetX.SetInteractor(iact)
planeWidgetX.On()
planeWidgetY.SetInteractor(iact)
planeWidgetY.On()
planeWidgetZ.SetInteractor(iact)
planeWidgetZ.On()

# vtk_show(renderer)



renderer.ResetCamera()
cam1 = renderer.GetActiveCamera()
cam1.Elevation(110)
cam1.SetViewUp(0, 0, -1)
cam1.Azimuth(45)
renderer.ResetCameraClippingRange()

iact.Initialize()
iact.Start()
render_window.Render()
