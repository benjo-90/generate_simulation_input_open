# Generate simulation input for dPETSTEP

Uses PET scans with brain tumors, background masks (BGs), tumor VOIs (VOIs) and pmod transformation files to create <br>
a set of altered PET scans, in which different tumors and tumor-free brains are combined. These scans can be used in <br>
dPETSTEP to create realistic brain tumor PET scans, e.g. for transfer learning in Deep Learning applications.

## General information

* All input and output images are 3D nifti files (.nii), except for the brain mask segments and tumor mask segments <br>
(*nr_of_segments*-dimensional). 
  

* Wrote and tested with Python 3.8.2 including the following packages:

   * SimpleITK 1.2.4
   * numpy 1.19
   * scipy 1.5.4
   * tqdm 4.48.0


* Furthermore PETPVC is needed (https://github.com/UCL/PETPVC) <br>
For Windows: go to "Releases", install "PETPVC-1.2.4-win.exe" and add "PETPVC/bin" to your path. <br>
Not tested on Linux yet.
  

* Only able to segment all tumors with *time_range* "FET_20_40" (TBR and Act) (see step 1 below).


* Variable *overwrite*, found at the top of nearly every script, is set to *False* so after the occuring of any errors <br>
during execution you don't have to process all the data again when rerunning the script.


* So far you need to manually check the combined brain/tumor images at the end and sort out and maybe write down nonsensical <br>
brain/tumor combinations.

## Steps

1. Set the following variables in **config.py**:
   * *data_path*: path to empty data directory
   * *PET_dir*, e.g. "PET_TBR"
   * *time_range*, e.g. "FET_20_40"
   * *lower_threshold_tumor* and *upper_threshold_tumor* (TBR default: 1.6 and e.g. 5000)
   
1. Run **create_dirs.py**.

1. Copy files in *data_path*:
   * PET scans into *data_path/PET_dir/time_range*
   * BGs into *data_path*/BG
   * VOIs into *data_path*/Conf
   
1. Before running **rename_files.py** make sure that the patient number in the filenames is between 1st and 2nd "_". <br>
   Uncomment code before and comment code again after running the script to prevent unwanted multiple renaming.
   
1. Run **exclude_patients.py** to remove PET scans, BGs and VOIs from patients not found in **included_Pat_newly_diagnosed.csv**. <br>
   Makes also sure that PET scans, BGs and VOIs match by moving files in correspondig subdirs in *excluded_files* which are not in the intersection of this three sets.
   
1. Run **center_PETs.py** and **center_VOIs_and_BGs.py**.<br>
   Extracting the exact transformation parameters from the pmod transformation file still needs to be fixed.
   
1. Run **mirror_healthy_hemispheres.py**.<br>
   Tumors in centered PET scans with patient numbers found in **not_for_brain.txt** extend over both hemispheres. <br>
   These PET scans are ignored by the script
   
1. Run **get_centered_tumor_masks.py** (and **get_centered_tumors.py**).<br>
   If you are dealing with activity units set *normalize* to True or change *lower_threshold_tumor*<br>
   in **config.py** accordingly.
   If you get an error regarding VOI 064, fix its spacing with the corresponding code lines in **error_fixes.py**.<br>
   If you get solely zeros for tumor 205, 231 and/or 315, fix the value range in the corresponding BGs and centered BGs <br>
   from 0-2 to 0-1 with the code lines in **error_fixes.py**
   
1. Specify *nr_of_segments* and *threshold_mode* (default: adapted) in **create_brain_mask_segments.py** and **create_tumor_masks_segments.py** and run them. <br>
   Creates *nr_of_segments*-dimensional brain and tumor masks (outer-brain-area included in *nr_of_segments*). <br>
   These are necessary for PETPVC in the next step. <br>
   Brain example: output dir "b_20210109_seg_9_adapted" in "FET_20_40_mirrored_brain_masks_segments"
   
1. Specify "method" in **pvc_brains.py** and **pvc_tumors.py** (only "GTM" and "RBV" tested so far) and run them. <br>
   In the file dialog you need to choose the brain/tumor masks segments dir created before, e.g. "b_20210109_seg_9_adapted".
   
1. Specify *mode* in **insert_tumor.py** and run it. In the file dialgs choose the PVC brains and PVC tumors (or tumor masks, <br>
   depending on the chosen mode). More details regarding the modes are found in the doc. Set seed if you want. <br>
   Brains and tumors are combined such that every tumor is used once so far. <br>
   UPDATE: If you choose modes[4] ("replace_original_with_matching_brain"):
   All tumors are inserted in their corresponding mirrored brain if available. The other tumors are randomly inserted in the remaining brains
   such that in total every brain is used not more than twice. 
   Check afterwards for unrealistic tumor/brain combinations and list them in "unrealistic_combis.txt"
   After running the script again, these combinations are avoided. If you found realistic combinations (through multiple execution or whatever),
   simply put them in "realistic_combis.txt" (already done for seed=1) and run again.
   
1. Run **create_mumaps.py** to create attenuation maps saved in *data_path/mumaps* of the mirrored PET scans. <br>
   By default values between 0 and 0.3 are set to zero, all others are set to 0.096 (attenuation factor of 511 keV photons in water). <br>
   The mumaps are needed for the simulation of realistic PET scans with inserted tumors in dPETSTEP.
