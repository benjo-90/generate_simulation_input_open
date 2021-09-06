"""Exclude invalid patient PET scans

Moves PET scans, VOIs and BGs of patients which are not part of the study
into subdir "invalid_patients" of dir "excluded_patients" (according to included_Pat_newly_diagn.csv)

Makes also sure that PET scans, BGs and VOIs match by moving files in corresponding subdirs in "excluded_files"
which are not in the intersection of this three sets.

Expected format: "Pat_007_BG.nii", "Pat_007_VOI.nii", "Pat_007.nii", "Pat_Act_007.nii"
"""


import os
import sys
import shutil
from config import data_path, PET_dir, time_range


with open("included_Pat_newly_diagn.csv") as file_csv:
    # csv_reader = csv.reader(file_csv)
    # for row in csv_reader:
    #     print(row)
    valid_pat_nrs = file_csv.read().split()

# turns e.g. 46 into 046
for i in range(len(valid_pat_nrs)):
    if len(valid_pat_nrs[i]) == 1:
        valid_pat_nrs[i] = "00" + valid_pat_nrs[i]
    elif len(valid_pat_nrs[i]) == 2:
        valid_pat_nrs[i] = "0" + valid_pat_nrs[i]

print("Nr of valid PET scans:", str(len(valid_pat_nrs)))


os.chdir(data_path)


patient_filenames = os.listdir(os.path.join(PET_dir, time_range))
patient_nrs = [patient_filename.rsplit(".")[0][-3:] for patient_filename in patient_filenames]
VOI_filenames = os.listdir("Conf")
VOI_nrs = [VOI_filename.rsplit(".")[0][-3:] for VOI_filename in VOI_filenames]
BG_filenames = os.listdir("BG")
BG_nrs = [BG_filename.rsplit(".")[0][-3:] for BG_filename in BG_filenames]

print("Nr of existing PET scans in '" + time_range + "':", str(len(patient_filenames)))
print("Nr of existing BGs in", "'BG':", str(len(BG_filenames)))
print("Nr of existing VOIs in", "'Conf':", str(len(VOI_filenames)) + "\n")


os.chdir(PET_dir)

# dirs only gets created if necessary
excluded_dir = os.path.join("excluded_files", "invalid_images")
no_scan_dir = os.path.join("excluded_files", "missing_PET_scan")
no_BG_dir = os.path.join("excluded_files", "missing_BG")
no_VOI_dir = os.path.join("excluded_files", "missing_VOI")

print("Checking for invalid PET scans, BGs and VOIs and moving them to 'invalid_images'...\n")
moved_PETs = []
pet_nrs = []
for i in range(len(patient_filenames)):
    if patient_nrs[i] not in valid_pat_nrs:
        if not os.path.isdir(excluded_dir):
            os.makedirs(excluded_dir)
        shutil.move(os.path.join(time_range, patient_filenames[i]), os.path.join(excluded_dir, patient_filenames[i]))
        moved_PETs.append(patient_filenames[i])
    else:
        pet_nrs.append(patient_nrs[i])
if moved_PETs:
    print("Moved", str(len(moved_PETs)), "invalid PET scans:")
    print(moved_PETs)
    print("\n")
else:
    print("No PET scans were moved\n")


moved_BGs_invalid = []
for BG_filename in BG_filenames:
    if BG_filename.rsplit(".")[0][-3:] not in valid_pat_nrs:
        if not os.path.isdir(excluded_dir):
            os.makedirs(excluded_dir)
        shutil.move(os.path.join("..", "BG", BG_filename), os.path.join(excluded_dir, BG_filename))
        moved_BGs_invalid.append(BG_filename)

if moved_BGs_invalid:
    print("Moved", str(len(moved_BGs_invalid)), "invalid BGs:")
    print(moved_BGs_invalid)
    print("\n")
else:
    print("No BGs were moved\n")


moved_VOIs_invalid = []
for VOI_filename in VOI_filenames:
    if VOI_filename.rsplit(".")[0][-3:] not in valid_pat_nrs:
        if not os.path.isdir(excluded_dir):
            os.makedirs(excluded_dir)
        shutil.move(os.path.join("..", "Conf", VOI_filename), os.path.join(excluded_dir, VOI_filename))
        moved_VOIs_invalid.append(VOI_filename)

if moved_VOIs_invalid:
    print("Moved", str(len(moved_VOIs_invalid)), "invalid VOIs:")
    print(moved_VOIs_invalid)
    print("\n")
else:
    print("No VOIs were moved\n")


patient_filenames = os.listdir(os.path.join(time_range))
patient_nrs = [filename.split(".")[0][-3:] for filename in patient_filenames]
BG_filenames = os.listdir(os.path.join("..", "BG"))
BG_nrs = [filename.split(".")[0][-3:] for filename in BG_filenames]
VOI_filenames = os.listdir(os.path.join("..", "Conf"))
VOI_nrs = [filename.split(".")[0][-3:] for filename in VOI_filenames]

print("Nr of existing PET scans in '" + time_range + "':", str(len(patient_nrs)))
print("Nr of existing BGs in", "'BG':", str(len(BG_nrs)))
print("Nr of existing VOIs in", "'Conf'", str(len(VOI_nrs)) + "\n")

if patient_nrs == VOI_nrs and patient_nrs == BG_nrs:
    print("PET scans, BGs and VOIs now match")
    sys.exit()

intersection = set(patient_nrs).intersection(set(VOI_nrs), set(BG_nrs))
print("Checking intersection of PET scans, BGs and VOIs and moving files which are not in it...\n")

# match PET scans with intersection
for patient_nr in patient_nrs:
    if patient_nr not in intersection:
        PET_name = "Pat_" + str(patient_nr) + ".nii"
        if patient_nr not in VOI_nrs:
            if not os.path.isdir(no_VOI_dir):
                os.makedirs(no_VOI_dir)
            shutil.move(os.path.join(time_range, PET_name), os.path.join(no_VOI_dir, PET_name))
        else:
            if not os.path.isdir(no_BG_dir):
                os.makedirs(no_BG_dir)
            shutil.move(os.path.join(time_range, PET_name), os.path.join(no_BG_dir, PET_name))

# match VOIs with intersection
for VOI_nr in VOI_nrs:
    if VOI_nr not in intersection:
        VOI_name = "Pat_VOI_" + str(VOI_nr) + ".nii"
        if not os.path.isdir(no_scan_dir):
            os.makedirs(no_scan_dir)
        shutil.move(os.path.join("..", "Conf", VOI_name), os.path.join(no_scan_dir, VOI_name))

# match BGs with intersection
for BG_nr in BG_nrs:
    if BG_nr not in intersection:
        BG_name = "Pat_BG_" + str(BG_nr) + ".nii"
        if not os.path.isdir(no_scan_dir):
            os.makedirs(no_scan_dir)
        shutil.move(os.path.join("..", "BG", BG_name), os.path.join(no_scan_dir, BG_name))


patient_filenames = os.listdir(os.path.join(time_range))
patient_nrs = [filename.split(".")[0][-3:] for filename in patient_filenames]
BG_filenames = os.listdir(os.path.join("..", "BG"))
BG_nrs = [filename.split(".")[0][-3:] for filename in BG_filenames]
VOI_filenames = os.listdir(os.path.join("..", "Conf"))
VOI_nrs = [filename.split(".")[0][-3:] for filename in VOI_filenames]

print("Nr of existing PET scans in '" + time_range + "':", str(len(patient_nrs)))
print("Nr of existing BGs in", "'BG':", str(len(BG_nrs)))
print("Nr of existing VOIs in", "'Conf'", str(len(VOI_nrs)) + "\n")

if patient_nrs == VOI_nrs and patient_nrs == BG_nrs:
    print("PET scans, BGs and VOIs now match")
    sys.exit()
else:
    print("Still no match!")
