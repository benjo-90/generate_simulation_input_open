"""Insert tumor in mirrored lesion-free brain

Combines tumors and tumor-free brains in such a way that every tumor is used once.
Set "reproducable" to True to set a seed.
Set "test_set" to True and set "test_nr" to only output "test_nr" images

Use tumor masks (e.g. "FET_20_40_tumor_masks") for modes "replace_value" and "mean"
Use PVC tumors (e.g. in "FET_20_40_tumors_pvc") for modes "add" and "replace_original"

"mean" sets the values in the volume specified by the correspondig tumor mask to the tumor mean value
calculated from the centered PET scan

"replace_value" sets the values in the volume specified by the corresponding tumor mask to "value"

"add" simply adds the pvc tumor with the brain. Scale tumor values by adjusting "scale"

"replace_original" simply puts the pvc tumor into the brain by replacing existing values
"""


import os
import random
import tkinter
from tkinter import filedialog
import SimpleITK as sitk
from tqdm import tqdm
import glob
import sys
from config import data_path, PET_dir, time_range

os.chdir(os.path.join(data_path, PET_dir))

modes = ["add", "replace_value", "mean", "replace_original", "replace_original_with_matching_brain"]
mode = modes[4]

test_set = False
reproducable = True
seed = 1

if reproducable:
    random.seed(seed)

if test_set:
    test_nr = 8

if mode == modes[0]:
    if time_range[-3:] == "Act":
        scale = 25000
    else:
        scale = 0.8

    suffix = "a" + str(scale)
    suffix = suffix.replace(".", "dot")

elif mode == modes[1]:
    if time_range[-3] == "Act":
        value = 8000
    else:
        value = 2.2

    suffix = "r" + str(value)
    suffix = suffix.replace(".", "dot")
    binary_filter = sitk.BinaryThresholdImageFilter()
    binary_filter.SetLowerThreshold(0)
    binary_filter.SetUpperThreshold(0)

elif mode == modes[2]:
    suffix = "mean"
    binary_filter = sitk.BinaryThresholdImageFilter()
    binary_filter.SetLowerThreshold(0)
    binary_filter.SetUpperThreshold(0)

elif mode == modes[3]:
    suffix = "r"
    binary_filter = sitk.BinaryThresholdImageFilter()
    binary_filter.SetLowerThreshold(0)
    binary_filter.SetUpperThreshold(0)

elif mode == modes[4]:
    suffix = "rm"
    binary_filter = sitk.BinaryThresholdImageFilter()
    binary_filter.SetLowerThreshold(0)
    binary_filter.SetUpperThreshold(0)

if time_range[-3:] == "Act":
    suffix_unit = "Act_"
else:
    suffix_unit = ""

if test_set:
    suffix += "_test"


root = tkinter.Tk()
root.withdraw()
brains_dir = filedialog.askdirectory(parent=root, initialdir=time_range + "_mirrored_pvc", title='Lesion-free brains').rsplit("/", 1)[-1]
if not brains_dir:
    sys.exit()
root = tkinter.Tk()
root.withdraw()
tumors_dir = filedialog.askdirectory(parent=root, initialdir=time_range + "_tumors_pvc", title='Tumors').split("/")[-1]
if not tumors_dir:
    sys.exit()

output_dir = os.path.join(time_range + "_inserted_tumors", tumors_dir + "_" + brains_dir + "_" + suffix)
print("Output dir before:", output_dir)
counter = 1
while os.path.isdir(output_dir):
    if counter == 1:
        output_dir += "_1"
    else:
        output_dir = output_dir[:-1] + str(counter)
    counter += 1
os.makedirs(output_dir)
print("Output dir after:", output_dir)

print(os.getcwd())

if mode == modes[1] or mode == modes[2]:
    os.chdir(os.path.join(tumors_dir))
    tumor_filenames = glob.glob("*.nii")
    os.chdir(os.path.join("..", time_range + "_mirrored_pvc", brains_dir))
    brain_filenames = glob.glob("*.nii")
    os.chdir(os.path.join("..", ".."))
else:
    os.chdir(os.path.join(time_range + "_tumors_pvc", tumors_dir))
    tumor_filenames = glob.glob("*.nii")
    os.chdir(os.path.join("..", "..", time_range + "_mirrored_pvc", brains_dir))
    brain_filenames = glob.glob("*.nii")
    os.chdir(os.path.join("..", ".."))

print(os.getcwd())
print(tumor_filenames)
print(brain_filenames)

if mode == modes[4]:
    matching_tumors = []
    matching_brains = []
    remaining_tumors = []
    not_use_again = []

    print(f"len(brain_filenames){len(brain_filenames)}")
    print(f"len(tumor_filenames){len(tumor_filenames)}")
    print(f"len(matching_tumor_list){len(matching_tumors)}")
    print(f"len(matching_brain_list){len(matching_brains)}")
    print(f"len(remaining_tumors){len(remaining_tumors)}")
    print(f"len(not_use_again){len(not_use_again)}")

    for brain_filename in brain_filenames:
        brain_nr = brain_filename.split("_")[2]
        i=0
        for tumor_filename in tumor_filenames:
            if brain_nr in tumor_filename:
                matching_tumors.append(tumor_filename)
                matching_brains.append(brain_filename)
                if i == 1:
                    not_use_again.append(brain_filename)
                i += 1
                if i == 2:
                    break
    for tumor_filename in tumor_filenames:
        if tumor_filename not in matching_tumors:
            remaining_tumors.append(tumor_filename)

    # print(brain_filenames)
    # print(matching_tumors)
    # print(matching_brains)
    # print(remaining_tumors)
    # print(not_use_again)
    #
    print("\n")
    print(f"len(brain_filenames){len(brain_filenames)}")
    print(f"len(tumor_filenames){len(tumor_filenames)}")
    print(f"len(matching_tumor_list){len(matching_tumors)}")
    print(f"len(matching_brain_list){len(matching_brains)}")
    print(f"len(remaining_tumors){len(remaining_tumors)}")
    print(f"len(not_use_again){len(not_use_again)}")

    for brain_to_remove in not_use_again:
        if brain_to_remove in brain_filenames:
            brain_filenames.remove(brain_to_remove)

    # print(f"len(brain_filenames){len(brain_filenames)}")
    #
    # print(type(brain_filenames))
    random.shuffle(remaining_tumors)
    random.shuffle(brain_filenames)
    # print(type(brain_filenames))

    brain_filenames_cleared = brain_filenames[:len(remaining_tumors)]
    brain_filenames_rest = brain_filenames[len(remaining_tumors):]

    print(remaining_tumors)
    print(brain_filenames_cleared)
    print(f"len(brain_filenames_cleared): {len(brain_filenames_cleared)}")
    print(f"len(remaining_tumors): {len(remaining_tumors)}")

    realistic_combis = {}
    with open(os.path.join("..", "..", "realistic_combis_seed_" + str(seed) + ".txt"), "r") as file:
        realistic_content = file.readlines()
    realistic_content = [line.split("\n")[0] for line in realistic_content]

    for line in realistic_content:
        key = line.split("_")[0]
        value_list = []
        value = line.split("_")[1]
        realistic_combis[key] = value
    print(realistic_combis)

    for i in range(len(remaining_tumors)):
        tumor_nr = remaining_tumors[i].split("_")[-2]
        if tumor_nr in list(realistic_combis.keys()):
            print(f"For tumor {tumor_nr}: changed brain {brain_filenames_cleared[i]} to...")
            splitted_brain_name = brain_filenames_cleared[i].split("_")
            splitted_brain_name[-2] = realistic_combis[tumor_nr]
            brain_filenames_cleared[i] = "_".join(splitted_brain_name)
            print(f"...{brain_filenames_cleared[i]}")


    unrealistic_combis = {}
    print(os.getcwd())
    with open(os.path.join("..", "..", "unrealistic_combis_seed_" + str(seed) + ".txt"), "r") as file:
        unrealistic_content = file.readlines()
    unrealistic_content = [line.split("\n")[0] for line in unrealistic_content]

    for line in unrealistic_content:
        key = line.split("_")[0]
        value_list = []
        value = line.split("_")[1:]
        unrealistic_combis[key] = value

    print(f"len(brain_filenames_rest) begin: {len(brain_filenames_rest)}")
    # remove unrealistic combinations (using "unrealistic_combis.txt")
    n_unrealistic_combis = 0
    for i in range(len(remaining_tumors)):
        # print(f"Now considering: \t {remaining_tumors[i]} and")
        # print(f"\t \t \t \t \t {brain_filenames_cleared[i]}")
        tumor_nr = remaining_tumors[i].split("_")[-2]
        brain_nr = brain_filenames_cleared[i].split("_")[-2]
        # print(f"Tumor nr: {tumor_nr}")
        # print(f"Brain nr: {brain_nr}")
        if tumor_nr in list(unrealistic_combis.keys()):
            # print(f"{tumor_nr} IS in unrealistic_combis.txt")
            if brain_nr in unrealistic_combis[tumor_nr]:
                # print(f"{brain_nr} IS NOT realistic")
                while brain_nr in unrealistic_combis[tumor_nr]:
                    new_brain = random.choice(brain_filenames_rest)
                    # print(f"Try to use another brain from brain_filenames_rest: {new_brain}")
                    brain_nr = new_brain.split("_")[-2]
                # print(f"New brain_nr: {brain_nr}")
                brain_filenames_cleared[i] = new_brain
                brain_filenames_rest.remove(new_brain)
                # print(f"{new_brain} removed from brain_filenames_rest")
                # print(f"len(brain_filenames_rest) new: {len(brain_filenames_rest)}")
                n_unrealistic_combis += 1
            # else:
                # print(f"{brain_nr} IS realistic")

        # else:
            # print(f"{tumor_nr} IS NOT in unrealistic_combis.txt")

    print(len(brain_filenames))
    print(len(remaining_tumors))

    matching_tumors.extend(remaining_tumors)
    matching_brains.extend(brain_filenames_cleared)

    tumor_filenames = matching_tumors
    brain_filenames = matching_brains

    # print(len(tumor_filenames))
    # print(len(brain_filenames))

else:
    random.shuffle(tumor_filenames)
    random.shuffle(brain_filenames)

    while len(brain_filenames) < len(tumor_filenames):
        brain_filenames.append(random.choice(brain_filenames))

CastFil = sitk.CastImageFilter()
CastFil.SetOutputPixelType(sitk.sitkFloat32)
stat_filter = sitk.LabelStatisticsImageFilter()

if test_set:
    z = zip(brain_filenames[:test_nr], tumor_filenames[:test_nr])
else:
    z = zip(brain_filenames, tumor_filenames)

for brain_name, tumor_name in tqdm(z):
    brain_image = sitk.ReadImage(os.path.join(time_range + "_mirrored_pvc", brains_dir, brain_name))
    if mode == modes[1] or mode == modes[2]:
        tumor_image = sitk.ReadImage(os.path.join(tumors_dir, tumor_name))
    else:
        tumor_image = sitk.ReadImage(os.path.join(time_range + "_tumors_pvc", tumors_dir, tumor_name))

    if mode == modes[2]:
        original_name = "centered_Pat_" + suffix_unit + tumor_name.split(".")[0][-3:] + ".nii"
        print(original_name)
        original_image = sitk.ReadImage(os.path.join(time_range + "_centered", original_name))
        stat_filter.Execute(original_image, tumor_image)
        tumor_mean = stat_filter.GetMean(1)

    tumor_image = CastFil.Execute(tumor_image)

    if mode == modes[1] or mode == modes[2]:
        output_filename = "t_" + tumor_name.split(".")[0].split("_")[-1] + "_b_" + brain_name.split("_")[-2] + ".nii"
    else:
        output_filename = "t_" + tumor_name.split("_")[-2] + "_b_" + brain_name.split("_")[-2] + ".nii"

    # output_filename += "_" + brains_dir_split[2]
    # output_filename += "_" + brains_dir_split[4][0:2] + "_" + brains_dir_split[6][0:2] + "_" + brains_dir_split[7]
    # output_filename += "_" + suffix + ".nii"
    output_name = os.path.join(output_dir, output_filename)

    if mode == modes[0]:
        sitk.WriteImage(brain_image + tumor_image * scale, output_name)
    else:
        reversed_tumor = binary_filter.Execute(tumor_image)
        reversed_tumor = CastFil.Execute(reversed_tumor)
        brain_hole = brain_image * reversed_tumor

        if mode == modes[1]:
            sitk.WriteImage(brain_hole + tumor_image * value, output_name)
        elif mode == modes[2]:
            sitk.WriteImage(brain_hole + tumor_image * tumor_mean, output_name)
        elif mode == modes[3] or mode == modes[4]:
            print(output_dir)
            print(output_name)
            sitk.WriteImage(brain_hole + tumor_image, output_name)

if mode == modes[4]:
    print(f"\nNr of combinations checked: {len(remaining_tumors)}")
    print(f"Nr of unrealistic combinations fixed: {n_unrealistic_combis}")


