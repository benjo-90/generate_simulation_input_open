"""Create mumaps

Creates mumaps from mirrored PET scans.
By default values between 0 and 0.3 are set to zero (outer-brain area),
all others are set to 0.096 1/cm (511 keV photons in water).
"""


import SimpleITK as sitk
import os
from tqdm import tqdm
from config import data_path, PET_dir, time_range

overwrite = False

os.chdir(data_path)
images_dir = os.path.join(PET_dir, time_range + "_mirrored")
output_dir = "mumaps"
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

filenames = os.listdir(images_dir)

binary_filter = sitk.BinaryThresholdImageFilter()
binary_filter.SetLowerThreshold(0)
binary_filter.SetUpperThreshold(0.3)
binary_filter.SetInsideValue(0)
binary_filter.SetOutsideValue(1)

CastFil = sitk.CastImageFilter()
CastFil.SetOutputPixelType(sitk.sitkFloat32)

for filename in tqdm(filenames):
    output_name = "mumap_" + filename[9:]

    if not overwrite and os.path.isfile(os.path.join(output_dir, output_name)):
        continue

    image = sitk.ReadImage(os.path.join(images_dir, filename))

    mumap = binary_filter.Execute(image)
    mumap = CastFil.Execute(mumap)*0.096

    sitk.WriteImage(mumap, os.path.join(output_dir, output_name))

