#!/usr/bin/env python
"""
==========================
VOI-Overlap-Analsis.py
==========================

The VOI-Overlap-Analsis.py integrates several interfaces to perform ...
"""

# import necessary modules
import sys
import time
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import SimpleITK as sitk
import FindFiles as ff

#main
start_time = time.time()

print("Script name: ", sys.argv[0])
print("Number of arguments: ", len(sys.argv))
print("The arguments are: ", str(sys.argv))

dataFolder = '/media/lkaiser/Backup/1_Projects_noSync/DFG_TSPO/Patient_Data/Auswertung/1_included/'

out = '/home/lkaiser/1_NUK/NUK0/DFG-TSPO/1_data/Auswertung/1_included/VOI-Overlap-Analysis/'
if os.path.isdir(out) is False:
    os.mkdir(out)
# end if

TumMaskSuf = '*Conf.nii'
BGMaskSuf = '*BG.nii'
FETSuf = '*FET_20_40.nii'
GE180Suf = '*GE1802FET_60_90.nii'
T1Suf = '*KM_T1_MRI2FET.nii'
T2Suf = '*T2_MRI2FET.nii'
imagesSuf = np.array([FETSuf, GE180Suf, T1Suf, T2Suf])

PatientDir = ff.FindDirOfFiles(np.concatenate((imagesSuf, np.array([TumMaskSuf, BGMaskSuf]))), dataFolder)


label_stat = sitk.LabelStatisticsImageFilter()
CastFil = sitk.CastImageFilter()
CastFil.SetOutputPixelType(sitk.sitkInt64)
# label_map = sitk.BinaryImageToLabelMapFilter()
# label_map.FullyConnectedOff()


def find_load(suf):
    file_reader = sitk.ImageFileReader()
    image_file = ff.FindPat(suf, Pat)[0]
    file_reader.SetFileName(image_file)
    image = file_reader.Execute()
    return image
# end def


def norm(image, mask_image):
    label_stat.Execute(image, mask_image)
    val = label_stat.GetMean(1)
    print('normalized to ', val)

    # scale = sitk.ShiftScaleImageFilter()
    # scale.SetScale(val)
    # norm_image = scale.Execute(image)

    nda = sitk.GetArrayFromImage(image)
    nda = np.nan_to_num(nda)/val
    norm_image = sitk.GetImageFromArray(nda)
    norm_image.CopyInformation(image)

    # label_stat.Execute(norm_image, mask_image)
    # print(label_stat.GetMean(1))

    return norm_image
# end def


def segment(image, confine_mask, lower, upper):
    # label_stat = sitk.LabelStatisticsImageFilter()
    # label_stat.Execute(image, confine_mask)
    mask_img = sitk.MaskImageFilter()
    # mask_img.SetMaskingValue(1.0)
    masked_image = mask_img.Execute(image, confine_mask)
    # sitk.Show(masked_image)

    # shape = image.GetSize()
    # print(shape[::-1])
    # print(image.GetSize())
    nda = sitk.GetArrayFromImage(masked_image)
    # print(nda.shape)
    ind = np.unravel_index(np.argmax(nda, axis=None), nda.shape)
    # print(np.max(nda))
    # print(nda[ind])
    # print(masked_image[(int(ind[2]), int(ind[1]), int(ind[0]))])
    seg = sitk.ConnectedThreshold(masked_image,
                                  seedList=[(int(ind[2]), int(ind[1]), int(ind[0]))],
                                  lower=lower, upper=upper)
    return seg
# end def


for Pat in PatientDir:
    pat_name = os.path.split(os.path.dirname(Pat))[1]
    print(pat_name)

    MaskImage = find_load(TumMaskSuf)
    MaskImage = CastFil.Execute(MaskImage)

    BGMaskImage = find_load(BGMaskSuf)
    BGMaskImage = CastFil.Execute(BGMaskImage)

    tbrImages = []
    for Suf in imagesSuf:
        # Suf = imagesSuf[0]
        # if Suf is not []:
        print(Suf)
        image_normalized = norm(find_load(Suf), BGMaskImage)
        image_seg = segment(image_normalized, MaskImage, 1.6, 1000000)

        tbrImages.append(image_normalized)
        # sitk.Show(image_seg, title=pat_name+Suf)
        # https://simpleitk.readthedocs.io/en/v1.2.4/Examples/ImageViewing/Documentation.html

    # end loop



# end loop


elapsed_time = time.time() - start_time
print(time.strftime("Elapsed time: %H:%M:%S", time.gmtime(elapsed_time)))